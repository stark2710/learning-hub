---
title: "Angular Architecture & CLI Setup"
module: "Angular Fundamentals"
domain: "Angular"
lesson_id: "frontend-mastery-angular-m1-l1-angular-architecture-cli-setup"
prev: ""
next: "frontend-mastery-angular-m1-l2-components-templates-data-binding"
duration: "~50 min"
---

```system_prompt
You are a senior frontend engineer with deep expertise in Angular internals, TypeScript, and enterprise web application architecture. The student is a backend developer (4+ years Java, 1+ year Python) who has just learned React basics and is now learning Angular. They understand component-based UI, TypeScript fundamentals, and OOP concepts well.

When answering questions:
- Draw parallels to both backend concepts (dependency injection, services) and React concepts they just learned
- Explain Angular's opinionated architecture vs React's flexibility
- Be precise about Angular-specific terminology (modules, decorators, zones)
- Highlight where Angular's Java/enterprise heritage shows through
- Always respond in plain English.
```

## What You'll Learn

- Why Angular is a full framework (not a library) and what that means for your codebase
- The mental model of Angular's module system and how it organizes code
- How decorators and TypeScript power Angular's architecture
- Setting up a production-ready Angular project with the CLI

```narration
Yaar, React seekhne ke baad Angular dekhoge toh pehle thoda overwhelming lagega. But backend developer ke liye Angular actually zyada familiar feel karega. Dependency injection hai, proper modules hain, TypeScript first-class citizen hai. Basically jaise Spring Boot ek opinionated framework hai Java ka, Angular waise hi frontend ka Spring Boot hai.
```

---

## The Mental Model

### React vs Angular: Library vs Framework

In React, you learned that React is a **library** — it handles the view layer, and you choose your own routing, state management, HTTP client, etc. Your `package.json` ends up with dozens of third-party dependencies.

Angular is a **framework** — it provides everything out of the box:

```
┌─────────────────────────────────────────────────────────────────┐
│                    REACT (Library Approach)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  React (view)  +  React Router  +  Redux  +  Axios  +  ...      │
│       ▲              ▲                ▲         ▲                │
│       │              │                │         │                │
│   You pick       You pick         You pick   You pick            │
│   and wire       and wire         and wire   and wire            │
│                                                                  │
│  Flexibility: HIGH    Learning curve: VARIES    Consistency: LOW │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   ANGULAR (Framework Approach)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    @angular/core                         │    │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │    │
│  │  │Components│ │ Services │ │   DI     │ │  Pipes   │   │    │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐        │
│  │  Router  │ │  Forms   │ │HttpClient│ │  Animations  │        │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘    │
│                                                                  │
│  All from Angular team. Designed to work together.              │
│                                                                  │
│  Flexibility: MEDIUM   Learning curve: HIGHER   Consistency: HIGH│
└─────────────────────────────────────────────────────────────────┘
```

For a Java developer, think of it this way:
- **React** = Using plain Java + picking Guice for DI + Gson for JSON + OkHttp for HTTP...
- **Angular** = Using Spring Boot where everything is integrated and opinionated

### Angular's Building Blocks

Angular has several key concepts that work together:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANGULAR APPLICATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    NgModule (Container)                  │    │
│  │                                                          │    │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │    │
│  │   │Component │  │Component │  │    Component     │     │    │
│  │   │  (View)  │  │  (View)  │  │     (View)       │     │    │
│  │   └────┬─────┘  └────┬─────┘  └────────┬─────────┘     │    │
│  │        │              │                 │               │    │
│  │        └──────────────┼─────────────────┘               │    │
│  │                       ▼                                  │    │
│  │              ┌─────────────────┐                        │    │
│  │              │    Service      │  ◄── Injected via DI   │    │
│  │              │  (Business      │                        │    │
│  │              │   Logic)        │                        │    │
│  │              └─────────────────┘                        │    │
│  │                                                          │    │
│  │   Directives   │   Pipes   │   Guards   │   Interceptors│    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

| Concept | What It Does | Java Equivalent |
|---------|--------------|-----------------|
| **Component** | UI + logic for a piece of the screen | Controller + View combined |
| **Service** | Business logic, data fetching | Service class |
| **Module** | Groups related components/services | Maven module or Spring @Configuration |
| **Directive** | Custom DOM behavior | (no direct equivalent) |
| **Pipe** | Transform data for display | Formatter/Converter |

```narration
Angular ka architecture dekho — modules hain jo components aur services group karte hain, dependency injection hai services inject karne ke liye, TypeScript decorators hain metadata define karne ke liye. Java developer ke liye yeh sab bahut familiar lagega. Spring ki tarah sochlo — @Component, @Service, @NgModule yeh sab Spring annotations jaisa hi kaam karte hain.
```

---

## How It Actually Works

### Project Structure

When you create an Angular project, you get this structure:

```
my-angular-app/
├── src/
│   ├── app/                          # Your application code
│   │   ├── app.component.ts          # Root component
│   │   ├── app.component.html        # Root component template
│   │   ├── app.component.css         # Root component styles
│   │   ├── app.component.spec.ts     # Root component tests
│   │   ├── app.module.ts             # Root module (bootstraps app)
│   │   └── app.routes.ts             # Route definitions
│   │
│   ├── index.html                    # Single HTML page (SPA entry)
│   ├── main.ts                       # Bootstrap point
│   ├── styles.css                    # Global styles
│   └── environments/                 # Environment configs
│       ├── environment.ts
│       └── environment.prod.ts
│
├── angular.json                      # Angular CLI configuration
├── package.json                      # NPM dependencies
├── tsconfig.json                     # TypeScript configuration
└── karma.conf.js                     # Test runner config
```

Compare this to React where you'd manually set up most of this structure. Angular gives you conventions.

### The Root Component

Every Angular app starts with a root component. Let's look at one:

```typescript
// app.component.ts
import { Component } from '@angular/core';

// The @Component decorator is metadata telling Angular 
// "this class is a component, here's how to render it"
@Component({
  selector: 'app-root',           // The HTML tag: <app-root></app-root>
  templateUrl: './app.component.html',  // Where to find the template
  styleUrls: ['./app.component.css']    // Where to find styles
})
export class AppComponent {
  // Class properties become template variables
  title = 'My Angular App';
  
  // Class methods can be called from template
  handleClick() {
    console.log('Button clicked!');
  }
}
```

```html
<!-- app.component.html -->
<main>
  <h1>Welcome to {{ title }}</h1>
  <button (click)="handleClick()">Click me</button>
</main>
```

Notice the differences from React:

| React | Angular |
|-------|---------|
| Function returns JSX | Class with decorator + separate HTML template |
| Props passed as arguments | Data as class properties |
| `onClick={handleClick}` | `(click)="handleClick()"` |
| `{variable}` | `{{ variable }}` |
| Single file (optional) | Separate files by default |

### Understanding Decorators

Angular uses TypeScript decorators heavily. If you know Java annotations, decorators work similarly:

```typescript
// Java annotation
@Service
@Transactional
public class UserService { }

// TypeScript decorator (Angular)
@Injectable({
  providedIn: 'root'  // Available application-wide
})
export class UserService { }
```

A decorator is a function that modifies a class. Angular's decorators add metadata that Angular reads at runtime:

```typescript
// This is what @Component actually does (simplified)
function Component(config) {
  return function(target) {
    // Attach metadata to the class
    target.__annotations__ = config;
    return target;
  }
}

// When you write:
@Component({ selector: 'app-root' })
export class AppComponent { }

// It's equivalent to:
class AppComponent { }
Component({ selector: 'app-root' })(AppComponent);
```

Common Angular decorators:
- `@Component` — Marks a class as a component
- `@Injectable` — Marks a class as available for DI
- `@NgModule` — Marks a class as a module container
- `@Input` / `@Output` — Component input/output bindings
- `@Directive` — Custom DOM behavior
- `@Pipe` — Data transformation

```narration
Decorators samajhna important hai. Java annotations ki tarah kaam karte hain — class pe metadata add karte hain jo framework runtime pe read karta hai. @Component bolta hai "yeh ek component hai", @Injectable bolta hai "isko dependency injection mein use kar sakte ho". Spring ke @Component, @Service jaisa hi concept hai.
```

---

### The Module System

Angular uses NgModules to organize code. Think of them as containers:

```typescript
// app.module.ts
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { HeaderComponent } from './header/header.component';
import { UserService } from './services/user.service';

@NgModule({
  // Components, directives, pipes that belong to this module
  declarations: [
    AppComponent,
    HeaderComponent
  ],
  
  // Other modules whose exports we need
  imports: [
    BrowserModule,      // Basic browser support
    HttpClientModule    // HTTP client
  ],
  
  // Services available throughout the app
  providers: [
    UserService
  ],
  
  // The root component to bootstrap
  bootstrap: [AppComponent]
})
export class AppModule { }
```

```
┌─────────────────────────────────────────────────────────────┐
│                        AppModule                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  declarations: [              imports: [                     │
│    AppComponent,  ◄─────┐       BrowserModule,              │
│    HeaderComponent      │       HttpClientModule            │
│  ]                      │     ]                              │
│                         │                                    │
│         ┌───────────────┘     (Brings in external modules'  │
│         │                      exported functionality)       │
│         │                                                    │
│  providers: [                 bootstrap: [                   │
│    UserService    ◄── DI        AppComponent  ◄── Start here│
│  ]                    registration                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Why modules matter:**
1. **Lazy loading** — Load feature modules only when needed
2. **Organization** — Group related components
3. **Encapsulation** — Control what's visible outside the module

Modern Angular (v14+) supports **standalone components** that don't require modules — similar to React. But most existing codebases use modules.

### Dependency Injection

Here's where Angular feels most like Spring:

```typescript
// user.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'  // Single instance for entire app
})
export class UserService {
  // HttpClient is automatically injected by Angular
  constructor(private http: HttpClient) { }
  
  getUsers(): Observable<User[]> {
    return this.http.get<User[]>('/api/users');
  }
}

// user-list.component.ts
import { Component, OnInit } from '@angular/core';
import { UserService } from '../services/user.service';

@Component({
  selector: 'app-user-list',
  template: `
    <ul>
      <li *ngFor="let user of users">{{ user.name }}</li>
    </ul>
  `
})
export class UserListComponent implements OnInit {
  users: User[] = [];
  
  // UserService is automatically injected!
  constructor(private userService: UserService) { }
  
  ngOnInit() {
    // Use the injected service
    this.userService.getUsers().subscribe(users => {
      this.users = users;
    });
  }
}
```

Compare to React where you'd manually pass services or use Context:

```jsx
// React - manual wiring
function UserList() {
  const userService = new UserService(); // Or from Context
  // ...
}
```

```narration
Dependency injection Angular ka best feature hai backend developers ke liye. Spring jaisa hai exactly — constructor mein type declare karo, Angular inject kar dega. Testing ke liye mock inject karo, production mein real service. Koi manual wiring nahi, koi props drilling nahi.
```

---

### Setting Up With Angular CLI

The Angular CLI handles project scaffolding, development server, testing, and production builds:

```bash
# Install Angular CLI globally
npm install -g @angular/cli

# Create new project
ng new my-app
# Interactive prompts:
# ? Would you like to add Angular routing? Yes
# ? Which stylesheet format? CSS (or SCSS)

# Navigate to project
cd my-app

# Start development server
ng serve
# Opens at http://localhost:4200 with hot reload

# Generate new component
ng generate component header
# Creates: header.component.ts, .html, .css, .spec.ts
# Updates: app.module.ts (adds to declarations)

# Generate service
ng generate service services/user
# Creates: user.service.ts, user.service.spec.ts

# Run tests
ng test

# Build for production
ng build --configuration=production
# Output in dist/ folder, optimized and minified
```

CLI commands follow patterns:

```
┌────────────────────────────────────────────────────────────────┐
│                     Angular CLI Commands                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ng new <name>           Create new project                    │
│  ng serve                Start dev server (port 4200)          │
│  ng build                Build for production                  │
│  ng test                 Run unit tests                        │
│  ng e2e                  Run end-to-end tests                  │
│                                                                 │
│  ng generate <type> <name>    (or ng g <type> <name>)         │
│  ─────────────────────────────────────────────────────────    │
│  ng g component header     → header/header.component.*         │
│  ng g service api          → api.service.ts                    │
│  ng g module feature       → feature/feature.module.ts         │
│  ng g directive highlight  → highlight.directive.ts            │
│  ng g pipe currency        → currency.pipe.ts                  │
│  ng g guard auth           → auth.guard.ts                     │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### The Bootstrap Process

How does Angular start your app?

```typescript
// main.ts - Entry point
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

// Bootstrap the root module
platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
```

```html
<!-- index.html - Single page for your SPA -->
<!doctype html>
<html>
<head>
  <title>My App</title>
</head>
<body>
  <!-- Angular finds this and replaces with AppComponent -->
  <app-root></app-root>
</body>
</html>
```

Bootstrap flow:

```
1. Browser loads index.html
            │
            ▼
2. main.ts runs, bootstraps AppModule
            │
            ▼
3. Angular reads AppModule metadata
   - What components to compile?
   - What services to register?
            │
            ▼
4. Angular finds <app-root> in index.html
            │
            ▼
5. Replaces <app-root> with AppComponent's template
            │
            ▼
6. Recursively instantiates child components
```

```narration
Bootstrap process samjho — main.ts module ko load karta hai, module components ko compile karta hai, phir index.html mein app-root tag dhundh ke AppComponent render kar deta hai. Spring Boot application startup jaisa hai — main method se sab shuru hota hai.
```

---

## The Rule

> **Angular is a framework, not a library. It provides structure, conventions, and integrated tooling. Follow its patterns — fighting them leads to pain.**

> **Components handle views, Services handle logic, Modules organize code, and Dependency Injection wires everything together.**

```narration
Angular ek complete framework hai. React ki tarah apne decisions lene ki zaroorat nahi — Angular already decide kar chuka hai routing, HTTP, forms, testing ke liye kya use karna hai. Iske patterns follow karo, fight mat karo. Bahut productivity milegi.
```

---

## Production Story

A developer coming from React created an Angular component that managed its own HTTP calls:

```typescript
// 🔴 Anti-pattern: Business logic in component
@Component({
  selector: 'app-user-profile',
  template: `<div>{{ user?.name }}</div>`
})
export class UserProfileComponent implements OnInit {
  user: User | null = null;
  
  // Direct HTTP call in component - React habit!
  constructor(private http: HttpClient) { }
  
  ngOnInit() {
    this.http.get<User>('/api/user/me')
      .subscribe(user => this.user = user);
  }
  
  updateUser(data: Partial<User>) {
    this.http.patch<User>('/api/user/me', data)
      .subscribe(user => this.user = user);
  }
  
  // Now this component can't be tested without mocking HttpClient
  // And the same API calls will be duplicated in other components
}
```

The code works but violates Angular's separation of concerns:

```typescript
// ✅ Fixed: Extract to service, inject where needed

// user.service.ts
@Injectable({ providedIn: 'root' })
export class UserService {
  private currentUser$ = new BehaviorSubject<User | null>(null);
  
  constructor(private http: HttpClient) { }
  
  getCurrentUser(): Observable<User> {
    return this.http.get<User>('/api/user/me').pipe(
      tap(user => this.currentUser$.next(user))
    );
  }
  
  updateUser(data: Partial<User>): Observable<User> {
    return this.http.patch<User>('/api/user/me', data).pipe(
      tap(user => this.currentUser$.next(user))
    );
  }
  
  // Cached value for components that just need current state
  get currentUser(): Observable<User | null> {
    return this.currentUser$.asObservable();
  }
}

// user-profile.component.ts
@Component({
  selector: 'app-user-profile',
  template: `<div>{{ user?.name }}</div>`
})
export class UserProfileComponent implements OnInit {
  user: User | null = null;
  
  // Inject service, not HttpClient
  constructor(private userService: UserService) { }
  
  ngOnInit() {
    this.userService.getCurrentUser()
      .subscribe(user => this.user = user);
  }
  
  updateUser(data: Partial<User>) {
    this.userService.updateUser(data)
      .subscribe(user => this.user = user);
  }
}
```

Benefits of the service approach:
1. **Testable** — Mock UserService, not HTTP
2. **Reusable** — Any component can inject UserService
3. **Cacheable** — Service can manage state
4. **Single responsibility** — Component handles view, service handles data

> **Warning:** In Angular interviews, expect questions about service design patterns. "Where does business logic go?" — always services, never components.

```narration
Yeh bahut common mistake hai React developers ki. React mein components mein fetch calls karna normal hai. Angular mein services mein jaani chahiye. Components sirf view handle karein, business logic services mein. Spring Controller aur Service ka separation yaad karo — same pattern hai.
```

---

## Going Deeper

### Zones and Change Detection

Angular uses Zone.js to automatically detect changes and update the DOM. Here's the magic:

```typescript
// Without Angular, you'd manually trigger updates:
button.addEventListener('click', () => {
  this.count++;
  this.updateDOM(); // Manual!
});

// Angular's Zone.js patches async APIs
// Click → Zone captures → Angular runs change detection → DOM updates
```

Zone.js patches browser APIs like:
- `setTimeout`, `setInterval`
- `addEventListener`
- `Promise.then`
- `XMLHttpRequest`

When any async operation completes, Zone tells Angular to check for changes:

```
┌─────────────────────────────────────────────────────────────┐
│                      Zone.js in Action                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User clicks button                                          │
│         │                                                    │
│         ▼                                                    │
│  Zone.js intercepts click event                              │
│         │                                                    │
│         ▼                                                    │
│  Your handler runs: this.count++                             │
│         │                                                    │
│         ▼                                                    │
│  Zone.js notifies Angular: "Async task finished"             │
│         │                                                    │
│         ▼                                                    │
│  Angular runs change detection from root                     │
│         │                                                    │
│         ▼                                                    │
│  Dirty components re-render                                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

This is why Angular feels "magical" compared to React where you explicitly call `setState`.

### AOT vs JIT Compilation

Angular has two compilation modes:

**JIT (Just-in-Time)** — Development mode:
- Templates compiled in browser
- Faster build, slower startup
- Includes compiler in bundle (~1MB extra)

**AOT (Ahead-of-Time)** — Production mode:
- Templates compiled at build time
- Slower build, faster startup
- Catches template errors early
- Smaller bundles (no compiler shipped)

```bash
# JIT (default for ng serve)
ng serve

# AOT (default for ng build --prod)
ng build --configuration=production
```

### Standalone Components (Angular 14+)

Modern Angular supports components without modules:

```typescript
// Standalone component - no module required
@Component({
  selector: 'app-header',
  standalone: true,  // New!
  imports: [CommonModule],  // Import what you need
  template: `<header>{{ title }}</header>`
})
export class HeaderComponent {
  title = 'My App';
}

// Bootstrap directly without AppModule
// main.ts
import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';

bootstrapApplication(AppComponent);
```

This moves Angular closer to React's simpler model while keeping DI and other features.

```narration
Standalone components naya feature hai jo Angular ko zyada React-like banata hai. Modules optional ho gaye hain. But existing codebases mein abhi bhi modules milenge, toh dono patterns samajhna important hai. New projects mein standalone components try kar sakte ho.
```

---

## Connecting the Dots

In this lesson, we established Angular's architecture: **framework mindset, modules, components, services, and DI**. We saw how it differs from React's library approach.

**Next lesson (Components, Templates & Data Binding)**: We'll dive deep into component syntax — property binding, event binding, two-way binding, and template syntax that's unique to Angular.

**Lesson 3 (Directives & Pipes)**: We'll learn about `*ngIf`, `*ngFor`, and how to create custom directives — Angular's way of extending HTML.

**Lesson 4 (Services & DI)**: We'll master Angular's dependency injection system — providers, injection tokens, and hierarchical injectors.

**Module 2 (Routing & State)**: We'll build on services to manage application state with RxJS and NgRx — Angular's reactive foundation.

The DI and service patterns you learned today will be essential for everything that follows. Unlike React where you might manually wire dependencies, Angular's DI pervades the entire framework.

```narration
Aaj framework architecture samjhi. Agle lesson mein components deeply explore karenge — data binding, template syntax, sab kuch. Angular mein templates React JSX se kaafi different hain. Phir directives aur pipes, aur uske baad services aur DI ka deep dive. Foundation strong rakhna!
```

---

## Practice

### Exercise 1: Project Structure Analysis

You've been given an Angular project to review. Identify what's wrong with this structure:

```
my-app/
├── src/
│   ├── app/
│   │   ├── app.component.ts      # Contains UserService code inline
│   │   ├── app.component.html
│   │   ├── app.module.ts
│   │   ├── login.component.ts    # Has HttpClient calls directly
│   │   ├── dashboard/
│   │   │   ├── dashboard.component.ts  # 500 lines, does everything
│   │   │   └── dashboard.component.html
│   │   └── shared/
│   │       └── utils.ts          # Random helper functions
```

What would you change and why?

<details>
<summary>Answer</summary>

**Problems identified:**

1. **UserService code in app.component.ts**
   - Services should be in separate files
   - Fix: Create `services/user.service.ts`

2. **HttpClient calls directly in login.component.ts**
   - Business logic shouldn't be in components
   - Fix: Create `services/auth.service.ts`

3. **500-line dashboard component**
   - Violates single responsibility principle
   - Fix: Split into multiple components: `DashboardComponent`, `DashboardHeaderComponent`, `DashboardStatsComponent`, etc.

4. **utils.ts with random helpers**
   - No organization, will become a dumping ground
   - Fix: Create specific services or group by purpose

**Improved structure:**

```
my-app/
├── src/
│   ├── app/
│   │   ├── core/                    # Singleton services
│   │   │   ├── services/
│   │   │   │   ├── user.service.ts
│   │   │   │   ├── auth.service.ts
│   │   │   │   └── api.service.ts
│   │   │   └── core.module.ts
│   │   │
│   │   ├── shared/                  # Reusable components/pipes
│   │   │   ├── components/
│   │   │   ├── pipes/
│   │   │   └── shared.module.ts
│   │   │
│   │   ├── features/                # Feature modules
│   │   │   ├── login/
│   │   │   │   ├── login.component.ts
│   │   │   │   └── login.module.ts
│   │   │   └── dashboard/
│   │   │       ├── dashboard.component.ts
│   │   │       ├── dashboard-header/
│   │   │       ├── dashboard-stats/
│   │   │       └── dashboard.module.ts
│   │   │
│   │   ├── app.component.ts
│   │   └── app.module.ts
```

**Key principles:**
- Services in `core/` for singletons
- Reusable UI in `shared/`
- Feature-based modules in `features/`
- Components <200 lines, single responsibility
</details>

### Exercise 2: CLI Commands

Write the CLI commands to accomplish these tasks:

1. Create a new Angular project called "todo-app" with routing and SCSS
2. Generate a component called "todo-item" in a "features/todo" folder
3. Generate a service called "todo" in a "core/services" folder
4. Build the project for production

<details>
<summary>Answer</summary>

```bash
# 1. Create new project with routing and SCSS
ng new todo-app --routing --style=scss

# Navigate into project
cd todo-app

# 2. Generate component in features/todo folder
ng generate component features/todo/todo-item
# Or shorthand:
ng g c features/todo/todo-item

# This creates:
# src/app/features/todo/todo-item/
#   ├── todo-item.component.ts
#   ├── todo-item.component.html
#   ├── todo-item.component.scss
#   └── todo-item.component.spec.ts

# 3. Generate service in core/services folder
ng generate service core/services/todo
# Or shorthand:
ng g s core/services/todo

# This creates:
# src/app/core/services/
#   ├── todo.service.ts
#   └── todo.service.spec.ts

# 4. Build for production
ng build --configuration=production
# Or shorthand: