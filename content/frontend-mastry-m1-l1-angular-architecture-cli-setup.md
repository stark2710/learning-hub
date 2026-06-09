---
title: "Angular Architecture & CLI Setup"
module: "Angular Fundamentals"
domain: "Frontend Mastry"
lesson_id: "frontend-mastry-m1-l1-angular-architecture-cli-setup"
prev: ""
next: "frontend-mastry-m1-l2-components-and-templates"
duration: "~50 min"
---

```system_prompt
You are a senior frontend architect with 14+ years of experience building enterprise Angular applications at scale. You have deep knowledge of Angular's architecture, dependency injection system, change detection mechanism, and the Angular compiler. You've migrated applications from AngularJS to modern Angular and have worked extensively with both module-based and standalone component architectures. When answering questions, always connect concepts back to how Angular actually works under the hood — the compilation process, the injector hierarchy, and zone.js. Explain the "why" behind Angular's design decisions, especially how it differs from React's approach. If the user asks about patterns, relate them to real enterprise production scenarios. Always respond in plain English. Use code examples liberally. If comparing to React (which the user has learned), be fair but highlight Angular's specific approach and when each makes sense.
```

## What You'll Learn

- Why Angular exists and what problems it solves differently than React
- The complete Angular architecture — modules, components, services, and how they wire together
- How the Angular CLI scaffolds, builds, and optimizes your application
- The mental model shift from React's "library" thinking to Angular's "framework" thinking

```narration
Chalo ab Angular ki duniya mein ghuste hain! React seekhne ke baad Angular seekhna interesting hoga kyunki yeh bilkul alag philosophy hai. React ek library hai — tum choose karte ho kaise state manage karna hai, kaise route karna hai. Angular ek complete framework hai — sab kuch built-in hai, ek specific way of doing things hai. Dono ka apna place hai, aur aaj hum samjhenge ki Angular ka architecture kyun aisa hai jaisa hai.
```

---

## The Mental Model

### React vs Angular: Library vs Framework

You've learned React. React is a UI library — it handles the view layer, and you bring everything else (routing, state management, HTTP calls). Angular is different:

```
┌─────────────────────────────────────────────────────────────────┐
│                     REACT ECOSYSTEM                              │
│                                                                  │
│   React (View) + React Router + Redux/Zustand + Axios + ...     │
│                                                                  │
│   You assemble your own stack. Flexibility is the feature.      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                     ANGULAR FRAMEWORK                            │
│                                                                  │
│   Components + Services + Router + HttpClient + Forms + DI +    │
│   RxJS + Testing + Animations + PWA + SSR + ...                 │
│                                                                  │
│   Everything included. Consistency is the feature.              │
└─────────────────────────────────────────────────────────────────┘
```

Neither is "better." React gives freedom; Angular gives structure. In large enterprise teams where 50 developers work on the same codebase, Angular's opinions prevent chaos. In a startup moving fast, React's flexibility lets you experiment quickly.

### The Angular Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ANGULAR APPLICATION                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Root Module (AppModule)                │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │ Components  │  │  Services   │  │  Directives │       │   │
│  │  │             │  │             │  │             │       │   │
│  │  │ AppComponent│  │ UserService │  │ HighlightDir│       │   │
│  │  │ HomeComp    │  │ AuthService │  │ CustomDir   │       │   │
│  │  │ NavComp     │  │ HttpService │  │             │       │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
│  │                                                           │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │   │
│  │  │   Pipes     │  │   Guards    │  │  Resolvers  │       │   │
│  │  │             │  │             │  │             │       │   │
│  │  │ DatePipe    │  │ AuthGuard   │  │ DataResolver│       │   │
│  │  │ CurrencyPipe│  │ RoleGuard   │  │             │       │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                   Feature Modules                         │   │
│  │  UserModule, ProductModule, AdminModule (lazy loaded)     │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

Let's break this down:

**Components** — The UI building blocks (like React components). Each component has a TypeScript class, an HTML template, and CSS styles.

**Services** — Business logic containers. Unlike React where you might put logic anywhere, Angular strictly separates UI (components) from logic (services).

**Modules** — Organizational containers that group related components, services, and other features. Think of them as feature boundaries.

**Directives** — Instructions that modify DOM behavior (like adding conditional classes, looping over elements).

**Pipes** — Data transformers for templates (format dates, currencies, custom transformations).

**Guards & Resolvers** — Route-level logic for authentication, authorization, and data fetching.

```narration
Dekho, React mein tum kuch bhi kahin bhi rakh sakte ho — bahut flexibility. Angular mein har cheez ka apna place hai. Component sirf UI handle karta hai, business logic service mein jaati hai, data transformation pipes mein hoti hai. Yeh separation of concerns bahut strict hai, aur yeh enterprise codebases mein bahut help karta hai jab 20-30 log same code pe kaam kar rahe hon.
```

---

## How It Actually Works

### The Angular Compilation Process

Unlike React where JSX compiles to JavaScript at build time, Angular has a more complex compilation story:

```
┌─────────────────────────────────────────────────────────────────┐
│                   ANGULAR COMPILATION PIPELINE                   │
│                                                                  │
│  TypeScript + Templates + Styles                                 │
│         ↓                                                        │
│  Angular Compiler (ngc) analyzes decorators and templates        │
│         ↓                                                        │
│  Generates JavaScript "component factories"                      │
│         ↓                                                        │
│  Ivy Renderer instructions (highly optimized)                    │
│         ↓                                                        │
│  Tree-shakeable output (unused code removed)                     │
└─────────────────────────────────────────────────────────────────┘
```

Angular uses **Ahead-of-Time (AOT) compilation** by default:

```typescript
// What you write
@Component({
  selector: 'app-hello',
  template: `<h1>Hello, {{name}}!</h1>`,
  styles: [`h1 { color: blue; }`]
})
export class HelloComponent {
  name = 'Angular';
}
```

```javascript
// What AOT compilation produces (simplified)
class HelloComponent {
  constructor() {
    this.name = 'Angular';
  }
}

// Ivy generates render instructions
function HelloComponent_Template(rf, ctx) {
  if (rf & 1) {  // Creation mode
    elementStart(0, 'h1');
    text(1);
    elementEnd();
  }
  if (rf & 2) {  // Update mode
    advance(1);
    textInterpolate('Hello, ', ctx.name, '!');
  }
}
```

**Why AOT matters:**
1. **Faster startup** — no compilation in the browser
2. **Smaller bundles** — compiler isn't shipped to users
3. **Earlier error detection** — template errors caught at build time
4. **Better security** — templates are pre-compiled, reducing XSS vectors

### Understanding Decorators

Angular heavily uses TypeScript decorators — metadata annotations that tell Angular how to process classes:

```typescript
// @Component decorator tells Angular:
// "This class is a component, use this selector, template, and styles"
@Component({
  selector: 'app-user-card',           // CSS selector to use in HTML
  templateUrl: './user-card.html',     // External template file
  styleUrls: ['./user-card.css'],      // External style files
  standalone: true,                     // New standalone approach
  imports: [CommonModule]               // Dependencies for template
})
export class UserCardComponent {
  @Input() user!: User;                 // Input property (like React props)
  @Output() delete = new EventEmitter<string>();  // Output event
}
```

Compare to React:

```jsx
// React - no decorators, just a function
function UserCard({ user, onDelete }) {
  return (
    <div className="user-card">
      <span>{user.name}</span>
      <button onClick={() => onDelete(user.id)}>Delete</button>
    </div>
  );
}
```

Angular's decorator approach:
- Explicit metadata that tooling can analyze
- Strong typing for inputs and outputs
- Clear separation of template and logic

```narration
Decorators Angular ka backbone hain. @Component decorator Angular ko batata hai ki "yeh class ek component hai, iski template yeh hai, styles yeh hain." Compile time pe Angular in decorators ko read karta hai aur optimized code generate karta hai. React mein yeh sab implicit hota hai function ke through, Angular mein explicit metadata hai.
```

### Setting Up with Angular CLI

The Angular CLI is not just a project generator — it's an entire development platform:

```bash
# Install Angular CLI globally
npm install -g @angular/cli

# Check version
ng version
# Angular CLI: 17.x.x
# Node: 20.x.x
# Package Manager: npm 10.x.x

# Create new project
ng new my-angular-app

# CLI asks questions:
# ? Which stylesheet format would you like to use? (CSS/SCSS/Sass/Less)
# ? Do you want to enable Server-Side Rendering (SSR)? (y/N)
# ? Do you want to enable Static Site Generation (SSG)? (y/N)
```

What `ng new` creates:

```
my-angular-app/
├── src/
│   ├── app/
│   │   ├── app.component.ts       # Root component class
│   │   ├── app.component.html     # Root component template
│   │   ├── app.component.css      # Root component styles
│   │   ├── app.component.spec.ts  # Unit tests
│   │   ├── app.config.ts          # Application configuration
│   │   └── app.routes.ts          # Route definitions
│   ├── index.html                 # Main HTML file
│   ├── main.ts                    # Application entry point
│   └── styles.css                 # Global styles
├── angular.json                   # CLI configuration
├── tsconfig.json                  # TypeScript configuration
├── package.json                   # Dependencies
└── karma.conf.js                  # Test runner configuration
```

### The Entry Point: main.ts

```typescript
// main.ts - Application bootstrap
import { bootstrapApplication } from '@angular/platform-browser';
import { appConfig } from './app/app.config';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent, appConfig)
  .catch((err) => console.error(err));
```

```typescript
// app.config.ts - Application-wide providers
import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { routes } from './app.routes';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),  // Change detection strategy
    provideRouter(routes),                                   // Routing
    provideHttpClient()                                      // HTTP client
  ]
};
```

Compare to React's entry point:

```jsx
// React - simpler entry
import ReactDOM from 'react-dom/client';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
```

Angular's entry point configures the entire application's infrastructure — routing, HTTP, change detection — before any component renders.

```narration
Dekho main.ts kitna important hai! React mein bas createRoot aur render — seedha point pe. Angular mein bootstrapApplication ke saath poora configuration jaata hai — routing, HTTP client, change detection strategy sab. Yeh upfront configuration Angular ka pattern hai — sab kuch explicit aur centralized.
```

### Your First Angular Component

```typescript
// app.component.ts
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',           // <app-root></app-root> in HTML
  standalone: true,                // Modern standalone approach
  imports: [RouterOutlet],         // Dependencies
  template: `
    <header>
      <h1>Welcome to {{ title }}!</h1>
      <nav>
        <a routerLink="/">Home</a>
        <a routerLink="/about">About</a>
      </nav>
    </header>
    <main>
      <router-outlet></router-outlet>
    </main>
  `,
  styles: [`
    header {
      background: #1976d2;
      color: white;
      padding: 1rem;
    }
    nav a {
      color: white;
      margin-right: 1rem;
    }
  `]
})
export class AppComponent {
  title = 'My Angular App';
}
```

Key differences from React:

| Aspect | React | Angular |
|--------|-------|---------|
| Template | JSX in same file | HTML (inline or separate file) |
| Styles | CSS modules, styled-components, etc. | Component-scoped CSS built-in |
| Data binding | `{value}` | `{{value}}` (interpolation) |
| Props | Function parameters | `@Input()` decorator |
| Events | `onClick={handler}` | `(click)="handler()"` |

---

## The Rule

> **Rule:** Angular is a platform, not just a library. It provides an opinionated, complete solution for building applications. Understanding its architecture upfront pays dividends as your app scales.

> **Corollary:** Components handle UI, Services handle logic, Modules handle organization. Violating this separation makes Angular fight you instead of help you.

> **Corollary:** The Angular CLI is not optional. It generates optimized builds, handles configuration, and enforces best practices. Use it.

---

## Production Story

### The Chaos of "Angular Without Angular"

A team I consulted for decided to "use Angular their own way." They had experience with React and didn't want to learn Angular's patterns:

```typescript
// ❌ The problematic approach
@Component({
  selector: 'app-user-dashboard',
  template: `
    <div *ngIf="loading">Loading...</div>
    <div *ngIf="!loading">
      <div *ngFor="let user of users">
        {{ user.name }}
      </div>
    </div>
  `
})
export class UserDashboardComponent implements OnInit {
  loading = true;
  users: User[] = [];
  
  // ❌ HTTP calls directly in component
  constructor(private http: HttpClient) {}
  
  ngOnInit() {
    // ❌ Raw HTTP call with no error handling
    this.http.get<User[]>('/api/users').subscribe(data => {
      this.users = data;
      this.loading = false;
    });
  }
  
  // ❌ Business logic in component
  calculateTotalSpending(user: User): number {
    return user.orders.reduce((sum, order) => sum + order.total, 0);
  }
  
  // ❌ Validation logic in component
  isHighValueCustomer(user: User): boolean {
    return this.calculateTotalSpending(user) > 10000;
  }
}
```

Problems:
1. Component became 500+ lines mixing UI, HTTP, and business logic
2. Impossible to test `calculateTotalSpending` without rendering the component
3. Same HTTP logic duplicated across 10 components
4. No loading/error states for HTTP failures

The Angular way:

```typescript
// ✅ user.service.ts - HTTP and business logic
@Injectable({
  providedIn: 'root'  // Singleton service, available app-wide
})
export class UserService {
  private apiUrl = '/api/users';
  
  constructor(private http: HttpClient) {}
  
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>(this.apiUrl).pipe(
      catchError(this.handleError)
    );
  }
  
  calculateTotalSpending(user: User): number {
    return user.orders.reduce((sum, order) => sum + order.total, 0);
  }
  
  isHighValueCustomer(user: User): boolean {
    return this.calculateTotalSpending(user) > 10000;
  }
  
  private handleError(error: HttpErrorResponse): Observable<never> {
    console.error('API Error:', error);
    return throwError(() => new Error('Something went wrong'));
  }
}
```

```typescript
// ✅ user-dashboard.component.ts - Just UI logic
@Component({
  selector: 'app-user-dashboard',
  standalone: true,
  imports: [CommonModule, UserCardComponent],
  template: `
    @if (loading) {
      <app-loading-spinner></app-loading-spinner>
    } @else if (error) {
      <app-error-message [message]="error"></app-error-message>
    } @else {
      <div class="user-grid">
        @for (user of users; track user.id) {
          <app-user-card 
            [user]="user"
            [isHighValue]="userService.isHighValueCustomer(user)"
          ></app-user-card>
        }
      </div>
    }
  `
})
export class UserDashboardComponent implements OnInit {
  users: User[] = [];
  loading = true;
  error: string | null = null;
  
  constructor(public userService: UserService) {}
  
  ngOnInit() {
    this.userService.getUsers().subscribe({
      next: (data) => {
        this.users = data;
        this.loading = false;
      },
      error: (err) => {
        this.error = err.message;
        this.loading = false;
      }
    });
  }
}
```

> **Warning:** Fighting Angular's architecture is a losing battle. The framework is designed around services for logic, components for UI. Mixing them works short-term but creates untestable, unmaintainable code. In interviews, showing clean separation of concerns demonstrates architectural maturity.

```narration
Yeh bahut common mistake hai — React mindset lekar Angular mein aana. React mein ek component mein sab kuch dal sakte ho, chalta hai. Angular mein yeh architecture violation hai. Service mein business logic, component mein sirf UI — yeh rule follow karo. Testing easy ho jaati hai, code reusable ho jaata hai, aur team mein kaam karna bahut smooth ho jaata hai.
```

---

## Going Deeper

### Zone.js and Change Detection

This is where Angular fundamentally differs from React. React uses explicit state updates (`setState`, `useState`). Angular uses **Zone.js** to automatically detect changes:

```typescript
// Zone.js wraps all async operations
// When any async operation completes, Angular knows to check for changes

@Component({
  selector: 'app-counter',
  template: `<button (click)="increment()">Count: {{ count }}</button>`
})
export class CounterComponent {
  count = 0;
  
  increment() {
    this.count++;  // No setState needed!
    // Zone.js detected the click event completed
    // Angular automatically triggers change detection
  }
}
```

How Zone.js works:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZONE.JS MONKEY-PATCHING                       │
│                                                                  │
│  Zone.js patches these browser APIs:                             │
│  • setTimeout / setInterval                                      │
│  • Promise.then                                                  │
│  • addEventListener                                              │
│  • XHR / fetch                                                   │
│  • And more...                                                   │
│                                                                  │
│  When ANY async operation completes:                             │
│  1. Zone.js notifies Angular                                     │
│  2. Angular runs change detection                                │
│  3. Updates DOM where bindings changed                           │
└─────────────────────────────────────────────────────────────────┘
```

This is both magical and problematic:
- **Pro:** No manual `setState` — just mutate properties
- **Con:** Every async operation triggers change detection (performance impact)

Angular 17+ introduced **Signals** as an alternative to Zone.js — we'll cover that in Module 6.

### Standalone vs Module Architecture

Angular historically used **NgModules** to organize code:

```typescript
// ❌ Old module-based approach (still works, but not recommended for new projects)
@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    FooterComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    RouterModule.forRoot(routes)
  ],
  providers: [UserService],
  bootstrap: [AppComponent]
})
export class AppModule {}
```

Angular 14+ introduced **standalone components** — simpler, more tree-shakeable:

```typescript
// ✅ Modern standalone approach
@Component({
  selector: 'app-header',
  standalone: true,                    // Self-contained
  imports: [CommonModule, RouterLink], // Own dependencies
  template: `...`
})
export class HeaderComponent {}

// No NgModule needed!
```

New projects should use standalone components. The Angular CLI generates standalone by default since Angular 17.

### The angular.json Configuration

```json
{
  "projects": {
    "my-app": {
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:application",
          "options": {
            "outputPath": "dist/my-app",
            "index": "src/index.html",
            "browser": "src/main.ts",
            "styles": ["src/styles.css"],
            "scripts": []
          },
          "configurations": {
            "production": {
              "budgets": [
                {
                  "type": "initial",
                  "maximumWarning": "500kB",   // Warn if bundle > 500KB
                  "maximumError": "1MB"         // Error if bundle > 1MB
                }
              ],
              "outputHashing": "all"           // Cache busting
            },
            "development": {
              "optimization": false,
              "sourceMap": true
            }
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "configurations": {
            "production": { "buildTarget": "my-app:build:production" },
            "development": { "buildTarget": "my-app:build:development" }
          },
          "defaultConfiguration": "development"
        }
      }
    }
  }
}
```

Key configurations:
- **budgets** — Enforce bundle size limits (crucial for performance)
- **sourceMap** — Enable for debugging
- **outputHashing** — Add hashes to filenames for cache invalidation

```narration
angular.json file bahut powerful hai — yahan se tum build process ko completely control kar sakte ho. Budgets bahut important hain production mein — agar bundle size badhta hai toh warning ya error milti hai. Yeh enterprise apps mein bahut zaroori hai jab performance matter karta hai.
```

---

## Connecting the Dots

This lesson establishes the Angular mental model. Here's how it connects forward:

**Next Lesson (Components & Templates):** We'll dive deep into component creation, template syntax (`*ngIf`, `*ngFor`, `@if`, `@for`), and how Angular's template parser works.

**Module 6 (Services & State):** Understanding that services are singletons by default (via `providedIn: 'root'`) is crucial. We'll explore the injector hierarchy and scoped providers.

**Module 7 (Routing & Forms):** The route guards and resolvers we mentioned are themselves services. The router integrates deeply with Angular's DI system.

**Compared to React:** You learned React's `UI = f(State)` model. Angular has a similar concept but with automatic change detection via Zone.js. In Module 6, we'll see how Signals bring Angular closer to React's explicit reactivity model.

---

## Practice

### Exercise 1: CLI Exploration

Create a new Angular project and explore its structure. Answer these questions:

1. What command generates a new component?
2. Where does the root component selector appear in the HTML?
3. What file configures the application's routes?

Run these commands and examine the output:

```bash
ng new practice-app --standalone --routing --style=css
cd practice-app
ng generate component features/user-profile
ng serve
```

<details>
<summary>Answer</summary>

1. `ng generate component <name>` (or `ng g c <name>` for short)

2. The root component selector (`app-root` by default) appears in `src/index.html`:
```html
<body>
  <app-root></app-root>
</body>
```

3. Routes are configured in `src/app/app.routes.ts`:
```typescript
import { Routes } from '@angular/router';

export const routes: Routes = [];
```

When you run `ng generate component features/user-profile`, it creates:
```
src/app/features/user-profile/
├── user-profile.component.ts
├── user-profile.component.html
├── user-profile.component.css
└── user-profile.component.spec.ts
```

The component is standalone by default and can be imported into any other component or route.

</details>

### Exercise 2: Compare Architectures

Given this React component, write the equivalent Angular component with proper service separation:

```jsx
// React component mixing concerns
function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch('/api/products')
      .then(res => res.json())
      .then(data => {
        setProducts(data);
        setLoading(false);
      });
  }, []);
  
  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(price);
  };
  
  if (loading) return <div>Loading...</div>;
  
  return (
    <ul>
      {products.map(p => (
        <li key={p.id}>{p.name} - {formatPrice(p.price)}</li>
      ))}
    </ul>
  );
}
```

<details>
<summary>Answer</summary>

**product.service.ts** — HTTP and utility logic:
```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

interface Product {
  id: number;
  name: string;
  price: number;
}

@Injectable({
  providedIn: 'root'
})
export class ProductService {
  private apiUrl = '/api/products';
  
  constructor(private http: HttpClient) {}
  
  getProducts(): Observable<Product[]> {
    return this.http.get<Product[]>(this.apiUrl);
  }
  
  formatPrice(price: number): string {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(price);
  }
}
```

**product-list.component.ts** — Just UI logic:
```typescript
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ProductService } from './product.service';

interface Product {
  id: number;
  name: string;
  price: number;
}

@Component({
  selector: 'app-product-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    @if (loading) {
      <div>Loading...</div>
    } @else {
      <ul>
        @for (product of products; track product.id) {
          <li>{{ product.name }} - {{ productService.formatPrice(product.price) }}</li>
        }
      </ul>
    }
  `
})
export class ProductListComponent implements OnInit {
  products: Product[] = [];
  loading = true;
  
  constructor(public productService: ProductService) {}
  
  ngOnInit() {
    this.productService.getProducts().subscribe(data => {
      this.products = data;
      this.loading = false;
    });
  }
}
```

**Key differences:**
- HTTP logic moved to `ProductService`
- Utility function `formatPrice` also in service (could also be a Pipe)
- Component only handles rendering and lifecycle
- Service injected via constructor (Dependency Injection)
- `track product.id` is Angular's equivalent of React's `key` prop

</details>

---

## Study Notes

**Q: Why does Angular use TypeScript while React can use plain JavaScript?**
Angular was designed from the ground up with TypeScript. Its heavy use of decorators (`@Component`, `@Injectable`) requires TypeScript's decorator support. The Angular compiler also relies on TypeScript's type information for AOT compilation and template type checking. While React works great with TypeScript, it's optional. Angular without TypeScript would lose core functionality.

**Q: When should I use Angular instead of React?**
Angular excels in large enterprise applications where consistency matters more than flexibility. If you have 20+ developers, long-term maintenance requirements, and need built-in solutions for routing, forms, HTTP, testing, and more — Angular's opinions prevent architecture fragmentation. React is better when you need flexibility, have a smaller team, or are building many small apps where you want to pick the best tool for each job.

**Q: What is the difference between standalone components and NgModules?**
NgModules were Angular's original way to organize code — you declared components in a module, imported dependencies, and exported what other modules could use. Standalone components (Angular 14+) are self-contained — each component declares its own imports. Standalone is simpler, more tree-shakeable (smaller bundles), and is now the recommended approach. NgModules still exist for backward compatibility and some advanced use cases (like lazy loading boundaries), but new code should use standalone.