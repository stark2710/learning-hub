---
title: "Understanding React's Component Model"
module: "React Foundations"
domain: "React"
lesson_id: "frontend-mastery-react-fundamentals-m1-l1-understanding-reacts-component-model"
prev: ""
next: "frontend-mastery-react-fundamentals-m1-l2-jsx-syntax-and-expressions"
duration: "~45 min"
---

```system_prompt
You are a senior frontend engineer with deep expertise in React internals, JavaScript, and UI architecture. The student is a backend developer (4+ years Java, 1+ year Python) learning React from scratch. They understand OOP, functions, and data structures well but are new to declarative UI paradigms.

When answering questions:
- Draw parallels to backend concepts they know (classes, objects, pure functions)
- Explain React's declarative model vs. imperative DOM manipulation
- Be precise about what "component" means in React vs. other frameworks
- Always respond in plain English.
```

## What You'll Learn

- Why React uses components as the fundamental building block (not templates or controllers)
- The mental shift from imperative DOM manipulation to declarative UI descriptions
- How function components work and why class components are now legacy
- What actually happens when React "renders" your component

```narration
Yaar, aaj hum React ka sabse fundamental concept samjhenge — components. Backend mein tumne classes aur functions likhe hain jo data process karte hain. React mein components wahi karte hain, but UI ke liye. Yeh samajhna bahut zaroori hai kyunki baaki sab kuch isi pe build hota hai.
```

---

## The Mental Model

Think about how you'd build a user profile card without any framework. In vanilla JavaScript, you'd write something like this:

```javascript
// Imperative approach: YOU tell the browser exactly what to do, step by step
function createProfileCard(user) {
  const div = document.createElement('div');
  div.className = 'profile-card';
  
  const img = document.createElement('img');
  img.src = user.avatar;
  div.appendChild(img);
  
  const name = document.createElement('h2');
  name.textContent = user.name;
  div.appendChild(name);
  
  // Now YOU must remember to update each element when user changes
  // And YOU must track which elements exist, which need updating...
  return div;
}
```

This is **imperative** programming — you're giving step-by-step instructions. It's like telling someone to cook by saying: "Turn on the stove. Get a pan. Put oil in pan. Wait 30 seconds. Crack an egg..."

React flips this entirely. You **describe** what the UI should look like for given data, and React figures out how to make it happen:

```jsx
// Declarative approach: YOU describe the end result, React handles the "how"
function ProfileCard({ user }) {
  return (
    <div className="profile-card">
      <img src={user.avatar} />
      <h2>{user.name}</h2>
    </div>
  );
}
```

This is **declarative** programming — you're describing the desired outcome. It's like giving someone a photo of the finished dish and saying "make this."

```
┌─────────────────────────────────────────────────────────────┐
│                    IMPERATIVE vs DECLARATIVE                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  IMPERATIVE (Vanilla JS)           DECLARATIVE (React)      │
│  ─────────────────────────         ──────────────────────   │
│                                                              │
│  1. Create div                     "Here's what the UI      │
│  2. Set class to 'card'             should look like for    │
│  3. Create img                      this data. You figure   │
│  4. Set src to avatar               out the DOM changes."   │
│  5. Append img to div                                        │
│  6. Create h2                                                │
│  7. Set text to name                                         │
│  8. Append h2 to div                                         │
│  9. When data changes...                                     │
│     find elements, update each                               │
│                                                              │
│  YOU manage state + DOM            REACT manages DOM         │
│  YOU track what changed            REACT tracks changes      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Why Components?

A **component** in React is simply a function that:
1. Takes data as input (called "props")
2. Returns a description of UI (JSX, which we'll cover next lesson)

That's it. A component is a **function from data to UI**.

```
         ┌─────────────┐
  props  │             │   UI description
 ───────►│  Component  ├───────────────────►
  (data) │  (function) │   (what to render)
         └─────────────┘
```

This is remarkably similar to pure functions you know from backend:
- Same input → same output
- No hidden state mutations
- Predictable and testable

```narration
Yeh mental model yaad rakho — component ek function hai jo data leta hai aur UI description return karta hai. Jaise backend mein pure function same input pe same output deta hai, React component bhi same props pe same UI describe karega. Yeh predictability bahut powerful hai.
```

---

## How It Actually Works

### The Simplest Component

```jsx
// A component is just a function that returns JSX
function Welcome() {
  return <h1>Hello, World!</h1>;
}

// To use it, you "call" it like an HTML tag
// (React handles the actual function call internally)
<Welcome />
```

When React sees `<Welcome />`, it:
1. Calls the `Welcome` function
2. Gets back the JSX description (`<h1>Hello, World!</h1>`)
3. Figures out what DOM operations are needed
4. Performs those operations efficiently

### Components with Props

Props are arguments to your component function. They're how parent components pass data down to children:

```jsx
// Props are received as the first argument
// We destructure them for cleaner code
function Welcome({ name, role }) {
  return (
    <div>
      <h1>Hello, {name}!</h1>
      <p>You are a {role}</p>
    </div>
  );
}

// Parent component passes props like HTML attributes
function App() {
  return (
    <div>
      <Welcome name="Amit" role="Backend Engineer" />
      <Welcome name="Priya" role="Frontend Engineer" />
    </div>
  );
}
```

```
┌─────────────────────────────────────────────────────────────┐
│                         App Component                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   <Welcome name="Amit" role="Backend Engineer" />           │
│        │                                                     │
│        │ props = { name: "Amit", role: "Backend Engineer" } │
│        ▼                                                     │
│   ┌─────────────────────────────────────────┐               │
│   │ function Welcome({ name, role }) {      │               │
│   │   return (                              │               │
│   │     <div>                               │               │
│   │       <h1>Hello, Amit!</h1>             │               │
│   │       <p>You are a Backend Engineer</p>│               │
│   │     </div>                              │               │
│   │   );                                    │               │
│   │ }                                       │               │
│   └─────────────────────────────────────────┘               │
│                                                              │
│   <Welcome name="Priya" role="Frontend Engineer" />         │
│        │                                                     │
│        ▼                                                     │
│   (same function, different props → different output)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Composing Components

The real power comes from nesting components within components:

```jsx
// Small, focused component
function Avatar({ imageUrl, size }) {
  return (
    <img 
      src={imageUrl} 
      width={size} 
      height={size}
      style={{ borderRadius: '50%' }}
    />
  );
}

// Uses Avatar component
function UserInfo({ user }) {
  return (
    <div className="user-info">
      <Avatar imageUrl={user.avatar} size={64} />
      <span>{user.name}</span>
    </div>
  );
}

// Uses UserInfo component
function Comment({ author, text, timestamp }) {
  return (
    <div className="comment">
      <UserInfo user={author} />
      <p className="comment-text">{text}</p>
      <span className="timestamp">{timestamp}</span>
    </div>
  );
}

// Top level uses Comment
function CommentList({ comments }) {
  return (
    <div className="comment-list">
      {comments.map(comment => (
        <Comment 
          key={comment.id}
          author={comment.author}
          text={comment.text}
          timestamp={comment.createdAt}
        />
      ))}
    </div>
  );
}
```

This creates a **component tree**:

```
CommentList
    │
    ├── Comment
    │       ├── UserInfo
    │       │       └── Avatar
    │       ├── <p> (comment text)
    │       └── <span> (timestamp)
    │
    ├── Comment
    │       └── ... (same structure)
    │
    └── Comment
            └── ... (same structure)
```

```narration
Dekho yeh component tree kaisa banta hai. Backend microservices ki tarah socho — har component apna ek kaam karta hai, aur dusre components use karte hain. Avatar sirf image handle karta hai, UserInfo user ki info, Comment poora comment. Isse code reusable aur maintainable banta hai.
```

---

### Function Components vs Class Components

You'll see two syntaxes in older React codebases:

```jsx
// MODERN: Function Component (use this!)
function Welcome({ name }) {
  return <h1>Hello, {name}</h1>;
}

// LEGACY: Class Component (understand it, don't write it)
class Welcome extends React.Component {
  render() {
    return <h1>Hello, {this.props.name}</h1>;
  }
}
```

Class components were the original way to write React. They have:
- `this.props` and `this.state` instead of function arguments
- Lifecycle methods like `componentDidMount`, `componentDidUpdate`
- More boilerplate and more ways to make mistakes

**Since React 16.8 (2019), function components can do everything class components can do** via Hooks. Today, class components are legacy — you'll maintain them in old codebases but never write new ones.

Why functions won:
- Less boilerplate
- No `this` binding issues (huge source of bugs)
- Hooks compose better than lifecycle methods
- Easier to test

```narration
Class components ko samajhna important hai kyunki purane codebases mein milenge. But naya code likhte waqt hamesha function components use karo. Hooks aane ke baad sab kuch functions mein ho sakta hai, aur yeh cleaner bhi hai.
```

---

## The Rule

> **Components are pure functions: same props → same UI. They describe what should appear, not how to make it appear. React handles the DOM manipulation.**

> **Think composition, not inheritance. Build complex UIs by combining simple components, not by extending base components.**

```narration
Yeh rule yaad rakho — components pure functions hain. Same input doge toh same output milega. Aur complex UI banane ke liye inheritance nahi, composition use karo. Chote components banao aur unhe combine karo.
```

---

## Production Story

A backend developer joined a frontend project and wrote this component for a notification badge:

```jsx
// 🔴 Bug: Treating component like an OOP class
function NotificationBadge({ count }) {
  // Trying to "cache" the previous value like a class field
  let previousCount = count;
  
  // Trying to check if count changed
  if (count !== previousCount) {
    console.log('Count changed!');
  }
  
  // This will NEVER log because previousCount is set to count on every render!
  // Each render, the function runs fresh. There are no persistent "fields"
  
  return <span className="badge">{count}</span>;
}
```

The developer expected `previousCount` to persist between renders like a class instance variable. But **every render is a fresh function call** — there are no persistent instance variables.

```jsx
// ✅ Fixed: Understanding that each render is a fresh call
// (For now, just show the count. We'll learn state persistence in Module 2)
function NotificationBadge({ count }) {
  // This function runs fresh every time React calls it
  // Variables declared here are NEW every render
  // For tracking changes, we'll need useRef or useEffect (coming soon!)
  
  return <span className="badge">{count}</span>;
}
```

The bug reveals a critical mental model difference:
- In OOP classes: instance lives, methods get called, fields persist
- In React functions: function gets called fresh each render, nothing persists automatically

> **Warning:** This "stateless per render" model is the #1 confusion point for developers coming from OOP backgrounds. Embrace it — it's what makes React predictable.

```narration
Yeh bahut common mistake hai. OOP background se aane wale developers class fields ki tarah sochte hain. But React component mein har render ek fresh function call hai. Kuch bhi automatically persist nahi hota. State aur refs ke through persistence hoti hai, woh agle modules mein seekhenge.
```

---

## Going Deeper

### What is JSX Really?

That HTML-like syntax isn't HTML — it's **JSX**, a syntax extension that gets transformed to JavaScript function calls:

```jsx
// What you write:
<div className="card">
  <h1>Hello</h1>
</div>

// What it becomes after compilation (Babel/TypeScript):
React.createElement('div', { className: 'card' },
  React.createElement('h1', null, 'Hello')
);
```

`React.createElement` returns a plain JavaScript object describing the element:

```javascript
// The object looks something like this:
{
  type: 'div',
  props: {
    className: 'card',
    children: {
      type: 'h1',
      props: {
        children: 'Hello'
      }
    }
  }
}
```

This object is called a **React Element**. It's just data describing what should be rendered — React reads this data and updates the DOM accordingly.

### Component vs Element

Don't confuse these:

```jsx
// Component: a FUNCTION that returns elements
function Welcome({ name }) {
  return <h1>Hello, {name}</h1>;
}

// Element: the RESULT of calling/rendering a component
const element = <Welcome name="Amit" />;
// element is an object: { type: Welcome, props: { name: "Amit" } }
```

- **Component**: The blueprint (function definition)
- **Element**: An instance created from that blueprint (function call result)

It's like the difference between a class definition and an object instance in Java.

### Why Return One Root Element?

You'll get an error if you try to return multiple elements without a wrapper:

```jsx
// 🔴 Error: Adjacent JSX elements must be wrapped
function Card() {
  return (
    <h1>Title</h1>
    <p>Content</p>
  );
}

// ✅ Fixed: Wrap in a single parent
function Card() {
  return (
    <div>
      <h1>Title</h1>
      <p>Content</p>
    </div>
  );
}

// ✅ Better: Use Fragment to avoid extra DOM element
function Card() {
  return (
    <>
      <h1>Title</h1>
      <p>Content</p>
    </>
  );
}
```

Why? Because a function can only return one value. `<> </>` is a Fragment — it groups elements without creating a DOM node.

```narration
JSX actually JavaScript mein transform hota hai. Har JSX tag ek React.createElement call ban jaata hai. Isliye ek hi root element return kar sakte ho — function ek hi value return karti hai. Fragment use karo agar extra wrapper div nahi chahiye.
```

---

## Connecting the Dots

In this lesson, we built the foundation: **components are functions that describe UI**. But we left some questions unanswered:

**Next lesson (JSX Syntax and Expressions)**: We'll dive deep into JSX — how to embed JavaScript expressions, handle attributes, and write clean JSX patterns.

**Lesson 3 (Props and Component Communication)**: We'll explore props patterns — default props, prop validation, and how data flows down the component tree.

**Module 2 (State and Lifecycle)**: We'll answer the persistence question — how do components remember things between renders? That's what `useState` is for.

**Module 3 (Advanced Hooks)**: We'll see how `useRef` can hold values that persist but don't trigger re-renders — solving the notification badge bug properly.

The declarative model you learned today is what enables React's advanced features: Virtual DOM diffing, concurrent rendering, and suspense all rely on components returning descriptions of UI, not directly manipulating the DOM.

```narration
Aaj humne component model samjha. Agle lesson mein JSX deeply explore karenge — expressions, attributes, sab kuch. Phir props patterns, aur uske baad state seekhenge jo components ko memory deta hai. Yeh foundation strong rakhna bahut important hai.
```

---

## Practice

### Exercise 1: Component Decomposition

Look at this monolithic component and break it into smaller, focused components:

```jsx
function ProductPage({ product }) {
  return (
    <div className="product-page">
      <div className="product-header">
        <img src={product.image} alt={product.name} />
        <div>
          <h1>{product.name}</h1>
          <p className="price">₹{product.price}</p>
          <div className="rating">
            {[1, 2, 3, 4, 5].map(star => (
              <span key={star}>{star <= product.rating ? '★' : '☆'}</span>
            ))}
            <span>({product.reviewCount} reviews)</span>
          </div>
        </div>
      </div>
      <div className="product-description">
        <h2>Description</h2>
        <p>{product.description}</p>
      </div>
      <div className="seller-info">
        <img src={product.seller.avatar} />
        <span>{product.seller.name}</span>
        <span>Verified Seller</span>
      </div>
    </div>
  );
}
```

<details>
<summary>Answer</summary>

```jsx
// Focused: Just handles star rating display
function StarRating({ rating, reviewCount }) {
  return (
    <div className="rating">
      {[1, 2, 3, 4, 5].map(star => (
        <span key={star}>{star <= rating ? '★' : '☆'}</span>
      ))}
      <span>({reviewCount} reviews)</span>
    </div>
  );
}

// Focused: Product image display
function ProductImage({ src, alt }) {
  return <img src={src} alt={alt} className="product-image" />;
}

// Combines image and basic product info
function ProductHeader({ product }) {
  return (
    <div className="product-header">
      <ProductImage src={product.image} alt={product.name} />
      <div>
        <h1>{product.name}</h1>
        <p className="price">₹{product.price}</p>
        <StarRating rating={product.rating} reviewCount={product.reviewCount} />
      </div>
    </div>
  );
}

// Focused: Description section
function ProductDescription({ description }) {
  return (
    <div className="product-description">
      <h2>Description</h2>
      <p>{description}</p>
    </div>
  );
}

// Focused: Seller info - reusable anywhere you show a seller
function SellerInfo({ seller }) {
  return (
    <div className="seller-info">
      <img src={seller.avatar} />
      <span>{seller.name}</span>
      <span>Verified Seller</span>
    </div>
  );
}

// Clean composition of focused components
function ProductPage({ product }) {
  return (
    <div className="product-page">
      <ProductHeader product={product} />
      <ProductDescription description={product.description} />
      <SellerInfo seller={product.seller} />
    </div>
  );
}
```

Key principles applied:
- Each component has a single responsibility
- StarRating and SellerInfo are reusable elsewhere
- ProductPage is now just composition
- Easier to test each piece in isolation
</details>

### Exercise 2: Mental Model Check

What's wrong with this code? Why doesn't the click counter work?

```jsx
function ClickCounter() {
  let count = 0;
  
  function handleClick() {
    count = count + 1;
    console.log('Clicked! Count is now:', count);
  }
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={handleClick}>Click me</button>
    </div>
  );
}
```

<details>
<summary>Answer</summary>

**The bug**: `let count = 0` is re-initialized to 0 on every render. When `handleClick` runs, it increments `count`, but that doesn't trigger a re-render. And even if it did, the re-render would reset `count` back to 0.

**Why it fails**:
1. `count` is local variable — it's created fresh each time `ClickCounter` runs
2. Modifying a local variable doesn't tell React to re-render
3. React only re-renders when **state** changes (using `useState`)

**The console.log IS working** — you'll see "Clicked! Count is now: 1" every time. But the UI never updates because:
- Changing a local variable doesn't trigger re-render
- Even if it did, `count` would reset to 0

**Correct solution** (you'll learn this in Module 2):

```jsx
import { useState } from 'react';

function ClickCounter() {
  // useState returns [value, setter] and persists across renders
  const [count, setCount] = useState(0);
  
  function handleClick() {
    // setCount tells React "re-render with new value"
    setCount(count + 1);
  }
  
  return (
    <div>
      <p>You clicked {count} times</p>
      <button onClick={handleClick}>Click me</button>
    </div>
  );
}
```

This exercise reinforces: **components are fresh function calls. For persistence, you need React's state management.**
</details>

---

## Study Notes

**Q: How is React's component model different from Angular's or Vue's?**
React uses plain JavaScript functions that return UI descriptions. Angular uses decorators and a class-based component model with templates. Vue uses single-file components with separate template/script/style sections. React's approach is more "JavaScript-first" — your component IS a function, not a class decorated with framework metadata.

**Q: When should I create a new component vs keep things in one component?**
Create a new component when: (1) a piece of UI is reused in multiple places, (2) a piece of logic becomes complex enough to deserve its own name/tests, (3) you want to isolate a piece of UI for performance (memoization). Don't over-split — if something is only used once and is simple, keeping it inline is fine.

**Q: Why does React use className instead of class?**
`class` is a reserved keyword in JavaScript (for class definitions). Since JSX is JavaScript, using `class` as an attribute would cause parsing issues. `className` maps to the DOM element's `className` property. Similarly, `htmlFor` is used instead of `for` on labels.