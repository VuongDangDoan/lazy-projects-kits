# React Native + Expo Patterns
> Stack: React Native 0.74 + Expo SDK 51 + TypeScript + React Navigation v6
> Type: mobile
> Slug: react-native-expo
>
> Copy to knowledge/L0-global/mobile-patterns.md during /onboard.
> After copying, customize: state management, API wrapper location, secure storage package.

## §index — Section Map

| §   | Topic | Load when |
|-----|-------|-----------|
| §1  | Stack invariants | ALWAYS |
| §2  | Navigation | Screen transitions, tabs, deep links |
| §3  | API service | HTTP calls, auth header injection |
| §4  | State management | Global/server/local state |
| §5  | Forms | Text inputs, validation, keyboard |
| §6  | Lists | FlatList, pull-to-refresh, pagination |
| §7  | Device APIs | Camera, location, notifications, biometrics |
| §8  | Offline & Caching | AsyncStorage, MMKV, sync |
| §9  | Permissions | expo-permissions, react-native-permissions |
| §10 | Platform differences | iOS vs Android |
| §11 | Common scenarios | Image upload, QR scanner, maps |
| §12 | Push Notifications | Expo Notifications + FCM/APNs |
| §15 | Anti-patterns | ALWAYS before writing code |

---

## §1 — Stack invariants

- HTTP: always use the project's `api()` wrapper (location: `src/services/api.ts`). Never `fetch` or `axios` directly
- Navigation: React Navigation v6 — `useNavigation<StackNavigationProp<RootStackParamList>>()` with typed params
- State:
  - Server state: React Query (TanStack Query) — `useQuery` / `useMutation`
  - Global UI state: Zustand store
  - Local component state: `useState` / `useReducer`
- Styling: `StyleSheet.create({})` only — no inline style objects (re-creates on every render)
- Secure storage: `expo-secure-store` for tokens/sensitive data. `AsyncStorage` for non-sensitive cache only
- Environment: `expo-constants` + `app.config.js` extra — never hardcode URLs
- Icons: `@expo/vector-icons` (Ionicons / MaterialIcons)

## §2 — Navigation

```typescript
// Type all route params in a centralized file: src/navigation/types.ts
export type RootStackParamList = {
  OrderList: undefined;
  OrderDetail: { orderId: string };
  CreateOrder: { customerId?: string };
};

// Navigate with typed params
const navigation = useNavigation<StackNavigationProp<RootStackParamList>>();
navigation.navigate('OrderDetail', { orderId: order._id });

// Get params in screen
const { orderId } = useRoute<RouteProp<RootStackParamList, 'OrderDetail'>>().params;

// Tab navigator — declare in src/navigation/TabNavigator.tsx
// Stack navigator per module — src/navigation/[Module]Navigator.tsx
// Deep links configured in app.json under "scheme" + linking config
```

## §3 — API service

```typescript
// src/services/api.ts
import axios from 'axios';
import * as SecureStore from 'expo-secure-store';

const api = axios.create({ baseURL: Constants.expoConfig?.extra?.apiUrl, timeout: 15000 });

api.interceptors.request.use(async (config) => {
  const token = await SecureStore.getItemAsync('access_token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (error) => {
    if (error.response?.status === 401) { /* redirect to login */ }
    return Promise.reject(error);
  }
);

export default api;

// Service functions — src/services/order.service.ts
export const orderService = {
  getList: (params: TQueryOrder) => api.get<TListResponse<TOrder>>('/v1/orders', { params }),
  getById: (id: string) => api.get<TSingleResponse<TOrder>>(`/v1/orders/${id}`),
  create: (body: TCreateOrder) => api.post<TSingleResponse<TOrder>>('/v1/orders', body),
  updateStatus: (id: string, status: string) => api.patch(`/v1/orders/${id}/status`, { status }),
};
```

## §4 — State management

```typescript
// Server state — React Query
const { data, isLoading, isError, refetch } = useQuery({
  queryKey: ['orders', params],
  queryFn: () => orderService.getList(params).then(r => r.data),
  staleTime: 30_000,
});

const mutation = useMutation({
  mutationFn: (body: TCreateOrder) => orderService.create(body).then(r => r.data),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['orders'] });
    Toast.show({ type: 'success', text1: 'Order created' });
    navigation.goBack();
  },
  onError: (err) => Toast.show({ type: 'error', text1: getErrorMessage(err) }),
});

// Global state — Zustand
// src/stores/authStore.ts
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      setUser: (user) => set({ user }),
      logout: () => set({ user: null }),
    }),
    { name: 'auth', storage: createJSONStorage(() => AsyncStorage) }
  )
);
```

## §5 — Forms

```typescript
// React Hook Form (if installed) or controlled inputs
const [name, setName] = useState('');
const [nameError, setNameError] = useState('');

const validate = (): boolean => {
  if (!name.trim()) { setNameError('Name is required'); return false; }
  return true;
};

// Keyboard avoiding — wrap screen in KeyboardAvoidingView
<KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'} style={{ flex: 1 }}>
  <ScrollView keyboardShouldPersistTaps="handled">
    <TextInput value={name} onChangeText={setName} />
  </ScrollView>
</KeyboardAvoidingView>
```

## §6 — Lists

```typescript
<FlatList
  data={orders}
  keyExtractor={(item) => item._id}
  renderItem={({ item }) => <OrderCard order={item} />}
  onRefresh={refetch}
  refreshing={isLoading}
  onEndReached={fetchNextPage}  // pagination
  onEndReachedThreshold={0.3}
  ListEmptyComponent={isLoading ? <Skeleton /> : <EmptyState text="No orders" />}
  ListFooterComponent={isFetchingNextPage ? <ActivityIndicator /> : null}
/>
```

## §7 — Device APIs

### Camera (expo-camera)
```typescript
const { status } = await Camera.requestCameraPermissionsAsync();
if (status !== 'granted') { Alert.alert('Camera permission required'); return; }
```

### Location (expo-location)
```typescript
const { status } = await Location.requestForegroundPermissionsAsync();
const location = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
```

## §8 — Offline & Caching

```typescript
// MMKV (fast) for non-sensitive cache
import { MMKV } from 'react-native-mmkv';
export const storage = new MMKV();
storage.set('key', JSON.stringify(data));
const data = JSON.parse(storage.getString('key') ?? 'null');

// expo-secure-store for tokens
await SecureStore.setItemAsync('token', value);
const token = await SecureStore.getItemAsync('token');
```

## §9 — Permissions

- Always request at point of use (not on app launch)
- Always handle denied case — show explanation + link to settings
- Permissions declared in `app.json` under `ios.infoPlist` (iOS) and `android.permissions` (Android)

## §10 — Platform differences

```typescript
import { Platform } from 'react-native';

// Platform-specific styles
const styles = StyleSheet.create({
  header: {
    paddingTop: Platform.OS === 'ios' ? 50 : 20,
    ...Platform.select({ ios: { shadowOpacity: 0.1 }, android: { elevation: 4 } }),
  },
});

// Platform-specific component
const Button = Platform.OS === 'ios' ? IOSButton : AndroidButton;

// Safe area
import { useSafeAreaInsets } from 'react-native-safe-area-context';
const insets = useSafeAreaInsets();
```

## §11 — Common scenarios

### Image upload
```typescript
const result = await ImagePicker.launchImageLibraryAsync({ mediaTypes: ImagePicker.MediaTypeOptions.Images });
if (!result.canceled) {
  const formData = new FormData();
  formData.append('file', { uri: result.assets[0].uri, name: 'photo.jpg', type: 'image/jpeg' } as any);
  await api.post('/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
}
```

### QR Scanner (expo-barcode-scanner)
```typescript
<BarCodeScanner onBarCodeScanned={({ data }) => handleScan(data)} style={StyleSheet.absoluteFillObject} />
```

## §12 — Push Notifications (Expo Notifications)

```typescript
// Register token
const token = await Notifications.getExpoPushTokenAsync();
await api.post('/users/push-token', { token: token.data });

// Handle notification tap (deep link)
Notifications.addNotificationResponseReceivedListener(response => {
  const { screen, params } = response.notification.request.content.data;
  navigation.navigate(screen, params);
});
```

## §15 — Anti-patterns

- Never `fetch` or `axios` directly — always use the `api` wrapper
- Never `AsyncStorage` for tokens — use `expo-secure-store`
- Never inline style objects `style={{ margin: 10 }}` — use `StyleSheet.create`
- Never request all permissions at app launch — lazy request at point of use
- Never use `useEffect` to sync derived state — use `useMemo`
- Never mutate navigation state directly — always use navigation actions
- Never assume iOS and Android behave the same for keyboards, safe areas, shadows
- Never skip `keyExtractor` on FlatList — causes rendering bugs
- Never store raw passwords or sensitive PII in any local storage
- Never hardcode API URLs — always use `app.config.js` extra fields
