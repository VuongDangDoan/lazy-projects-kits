# NestJS + TypeScript + PostgreSQL Patterns
> Stack: NestJS 10 + TypeScript 5 + TypeORM 0.3 + PostgreSQL 16
> Type: be
> Slug: nestjs-ts-pg
>
> Copy to knowledge/L0-global/be-patterns.md during /onboard.
> After copying, customize: DefaultEntity base class name, auth decorator, banned packages.

## §index — Section Map

| §   | Topic | Load when |
|-----|-------|-----------|
| §1  | Stack invariants | ALWAYS |
| §2  | Entity definition | Creating or modifying entities |
| §3  | DTOs | Creating request/response shapes |
| §4  | Service layer | Writing business logic |
| §5  | Controller | Writing HTTP endpoints |
| §6  | Module wiring | Registering new modules |
| §7  | Auth & Permissions | RBAC-gated routes |
| §8  | QueryBuilder | Complex list queries with filters |
| §9  | Transactions | Multi-table write operations |
| §10 | State machines | Entities with status transitions |
| §11 | Migrations | DB schema changes |
| §12 | Common scenarios | File upload, export, bulk ops |
| §14 | Anti-patterns | ALWAYS before writing code |

---

## §1 — Stack invariants

- NestJS decorators only — no raw Express middleware in modules
- Every module imports via `@Module({ imports: [], providers: [], controllers: [], exports: [] })`
- Auth: use the project's `@Auth()` decorator (wraps `@UseGuards`). Never use `@UseGuards` directly
- HTTP errors: `BadRequestException`, `NotFoundException`, `ForbiddenException`, `ConflictException` — never a custom `BusinessException`
- Events: direct service-to-service calls or `NotificationService` — do NOT use `@nestjs/event-emitter` (not installed)
- Do not import `Repository` directly — use the entity's TypeORM repository pattern via `@InjectRepository()`

## §2 — Entity definition

```typescript
// Every entity extends the project base entity (name may vary — check src/shared/)
@Entity('table_name')
export class OrderEntity extends DefaultEntity {
  @Column({ type: 'varchar', length: 50 })
  code: string;

  @Column({ type: 'enum', enum: EOrderStatus, default: EOrderStatus.PENDING })
  status: EOrderStatus;

  @Column({ type: 'uuid' })
  customerId: string;

  @ManyToOne(() => CustomerEntity)
  @JoinColumn({ name: 'customer_id' })
  customer: CustomerEntity;

  @OneToMany(() => OrderItemEntity, (item) => item.order, { cascade: true })
  items: OrderItemEntity[];
}

// DefaultEntity provides: _id (UUID PK), createdAt, updatedAt, createdBy, updatedBy
// Do NOT add: id, created_at, updated_at, deleted_at manually
// Do NOT use BIGSERIAL/auto-increment PKs
// Soft delete: use a status field (e.g. CANCELLED) — not deleted_at column
```

## §3 — DTOs

```typescript
// Request DTO — always use class-validator + class-transformer
export class CreateOrderDto {
  @ApiProperty({ example: 'John Doe' })
  @Expose()
  @IsString()
  @IsNotEmpty()
  customerName: string;

  @ApiPropertyOptional()
  @Expose()
  @IsOptional()
  @IsDateString()
  deliveryDate?: string;
}

// Query DTO — extend PaginationDto
export class QueryOrderDto extends PaginationDto {
  @ApiPropertyOptional()
  @Expose()
  @IsOptional()
  @IsString()
  status?: string;
}

// Response — plain class with @Expose() (not DTO, no validators)
export class OrderResponse {
  @Expose() _id: string;
  @Expose() code: string;
  @Expose() status: EOrderStatus;
  @Expose() @Type(() => Date) createdAt: Date;
}
```

## §4 — Service layer

```typescript
@Injectable()
export class OrderService {
  constructor(
    @InjectRepository(OrderEntity)
    private readonly orderRepo: Repository<OrderEntity>,
    private readonly customerService: CustomerService,
  ) {}

  async createOrder(dto: CreateOrderDto, userId: string): Promise<OrderEntity> {
    const customer = await this.customerService.findOneOrFail(dto.customerId);

    const order = this.orderRepo.create({
      ...dto,
      createdBy: userId,
      status: EOrderStatus.PENDING,
    });
    return this.orderRepo.save(order);
  }

  async findOneOrFail(id: string): Promise<OrderEntity> {
    const order = await this.orderRepo.findOne({ where: { _id: id } });
    if (!order) throw new NotFoundException(`Order ${id} not found`);
    return order;
  }
}
```

## §5 — Controller

```typescript
@Auth()  // always at controller level (applies to all routes)
@ApiTags('order')
@Controller('v1/orders')
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @Post()
  @ApiOperation({ summary: 'Create order' })
  async create(
    @Body() dto: CreateOrderDto,
    @GetUser() user: UserPayload,
  ): Promise<ApiResponse<OrderResponse>> {
    const order = await this.orderService.createOrder(dto, user.userId);
    return { data: plainToClass(OrderResponse, order, { excludeExtraneousValues: true }), message: 'Created' };
  }

  @Get()
  async findAll(
    @Query() query: QueryOrderDto,
  ): Promise<PaginatedResponse<OrderResponse>> {
    const [items, total] = await this.orderService.findAll(query);
    return { data: plainToClass(OrderResponse, items, { excludeExtraneousValues: true }), total, ...query };
  }
}

// Response shapes:
// Single: { data: {}, message: string }
// List:   { data: [], total: number, page: number, limit: number, message?: string }
// Error:  { message: string | string[], statusCode: number }
```

## §6 — Module wiring

```typescript
@Module({
  imports: [
    TypeOrmModule.forFeature([OrderEntity, OrderItemEntity]),
    forwardRef(() => CustomerModule),  // use forwardRef only for circular deps
  ],
  providers: [OrderService],
  controllers: [OrderController],
  exports: [OrderService],  // export only what other modules need
})
export class OrderModule {}
```

## §7 — Auth & Permissions

```typescript
// Route-level auth (applies to all routes in controller)
@Auth()  // authenticated, any role
@Auth('admin')  // specific role
@Auth('admin', 'manager')  // multiple roles — any of these

// Method-level permission override
@Auth('admin')  // on method — overrides controller-level

// Get current user in handler
@GetUser() user: UserPayload
// UserPayload: { userId: string, role: string, ... }
```

## §8 — QueryBuilder

```typescript
async findAll(query: QueryOrderDto): Promise<[OrderEntity[], number]> {
  const qb = this.orderRepo.createQueryBuilder('o')
    .leftJoinAndSelect('o.customer', 'c')
    .where('1=1');

  if (query.status) {
    qb.andWhere('o.status = :status', { status: query.status });
  }
  if (query.search) {
    qb.andWhere('(o.code ILIKE :search OR c.name ILIKE :search)', { search: `%${query.search}%` });
  }
  if (query.fromDate) {
    qb.andWhere('o.created_at >= :from', { from: query.fromDate });
  }

  return qb
    .orderBy(`o.${query.sortBy ?? 'created_at'}`, query.sortOrder ?? 'DESC')
    .skip((query.page - 1) * query.limit)
    .take(query.limit)
    .getManyAndCount();
}
```

## §9 — Transactions

```typescript
// Inject DataSource, not EntityManager
constructor(private readonly dataSource: DataSource) {}

async createWithItems(dto: CreateOrderDto): Promise<OrderEntity> {
  return this.dataSource.transaction(async (manager) => {
    const order = manager.create(OrderEntity, { ...dto });
    await manager.save(order);

    const items = dto.items.map(i => manager.create(OrderItemEntity, { ...i, orderId: order._id }));
    await manager.save(items);

    return order;
  });
}
```

## §10 — State machines

```typescript
// Allowed transitions map
const TRANSITIONS: Record<EOrderStatus, EOrderStatus[]> = {
  [EOrderStatus.PENDING]:    [EOrderStatus.CONFIRMED, EOrderStatus.CANCELLED],
  [EOrderStatus.CONFIRMED]:  [EOrderStatus.IN_PRODUCTION, EOrderStatus.CANCELLED],
  [EOrderStatus.IN_PRODUCTION]: [EOrderStatus.COMPLETED],
  [EOrderStatus.COMPLETED]:  [],
  [EOrderStatus.CANCELLED]:  [],
};

// Guard method — call before any status change
validateTransition(current: EOrderStatus, next: EOrderStatus): void {
  if (!TRANSITIONS[current]?.includes(next)) {
    throw new BadRequestException(
      `Cannot transition order from ${current} to ${next}`
    );
  }
}
```

## §11 — Migrations

```bash
# Generate migration (TypeORM CLI)
npx typeorm migration:generate src/migrations/AddOrderDeliveryDate -d src/data-source.ts

# Run migrations
npx typeorm migration:run -d src/data-source.ts
```

Rules:
- Additive only: ADD columns, ADD tables, ADD indexes — never DROP or RENAME without an ADR
- Nullable first: new columns on existing tables must be nullable initially
- Never edit a committed migration — always generate a new one

## §12 — Common scenarios

### File upload (multer)
```typescript
@Post('upload')
@UseInterceptors(FileInterceptor('file'))
async upload(@UploadedFile() file: Express.Multer.File) { ... }
```

### Excel export (exceljs)
```typescript
const wb = new ExcelJS.Workbook();
const ws = wb.addWorksheet('Data');
ws.addRows(data);
const buffer = await wb.xlsx.writeBuffer();
res.set({ 'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
res.send(buffer);
```

## §14 — Anti-patterns

- `@UseGuards(...)` directly — always use `@Auth()` wrapper
- `BusinessException` — does not exist; use NestJS built-in exceptions
- `@nestjs/event-emitter` — not installed; use direct service calls
- BIGSERIAL / auto-increment PK — always UUID via DefaultEntity
- `deleted_at` / `deletedAt` soft-delete column — use status field instead
- Raw SQL in service (`queryRunner.query()`) — use TypeORM QueryBuilder
- Empty `@Expose()` without `excludeExtraneousValues: true` in `plainToClass` — leaks fields
- `forwardRef` overuse — symptom of circular dependency; restructure module if possible
- Mutable `@Column` on DefaultEntity fields (`_id`, `createdAt`, etc.) — never override base fields
- Writing ticket/story IDs in code comments — use commit messages instead
