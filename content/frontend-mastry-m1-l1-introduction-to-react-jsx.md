---
title: "Introduction to React & JSX"
module: "React Fundamentals"
domain: "Frontend Mastry"
lesson_id: "frontend-mastry-m1-l1-introduction-to-react-jsx"
prev: ""
next: "frontend-mastry-m1-l2-components-and-props"
duration: "~45 min"
---

```system_prompt
You are a senior frontend engineer with 12+ years of experience building production React applications at scale. You have deep knowledge of React's internals, the virtual DOM reconciliation algorithm, and JSX compilation. When answering questions, always connect concepts back to how React actually works under the hood. Explain the "why" behind React's design decisions. If the user asks about patterns, relate them to real production scenarios. Always respond in plain English. Use code examples liberally. If comparing to vanilla JavaScript or other frameworks, be fair but highlight React's specific approach.
```

## What You'll Learn

- Why React exists and what problem it actually solves (hint: it's not "making websites")
- How JSX is just syntax sugar — and what it compiles down to
- The virtual DOM mental model that makes React fast
- How to think in components from day one

```narration
Chalo shuru karte hain React ki journey! Bahut log React ko sirf ek "library" samajhte hain, but actually yeh ek completely different way of thinking hai about building UIs. Aaj hum dekhnge ki React kyun exist karta hai, JSX actually kya hai behind the scenes, aur virtual DOM ka asli funda kya hai. Trust me, yeh foundation bahut important hai.
```

---

## The Mental Model

### The Problem React Solves

Before React, building dynamic UIs was painful. Let me show you why:

```javascript
// Vanilla JavaScript: The Pain
let todos = ['Learn React', 'Build App'];

function renderTodos() {
  const list = document.getElementById('todo-list');
  list.innerHTML = ''; // Clear everything
  
  todos.forEach((todo, index) => {
    const li = document.createElement('li');
    li.textContent = todo;
    li.onclick = () => deleteTodo(index);
    list.appendChild(li);
  });
}

function addTodo(text) {
  todos.push(text);
  renderTodos(); // Re-render EVERYTHING
}

function deleteTodo(index) {
  todos.splice(index, 1);
  renderTodos(); // Re-render EVERYTHING again
}
```

See the problem? Every tiny change triggers a complete rebuild of the UI. For a todo list, fine. For Facebook's news feed with thousands of elements? Disaster.

The real issues:
1. **Manual DOM manipulation** — you track what changed and update it yourself
2. **State scattered everywhere** — data lives in DOM, in variables, everywhere
3. **No clear data flow** — debugging becomes guesswork

### React's Big Idea

React's insight: **What if we described what the UI should look like, and let the library figure out how to update it?**

```
┌─────────────────────────────────────────────────────────┐
│                   YOUR MENTAL MODEL                      │
│                                                          │
│   State (Data)  ──────►  UI = f(State)  ──────►  Screen │
│                                                          │
│   When state changes, React re-computes the UI           │
│   and efficiently updates only what changed              │
└─────────────────────────────────────────────────────────┘
```

This is **declarative programming**. You declare what the UI should look like for any given state. React handles the imperative DOM updates.

```narration
Yaar yeh samajhna bahut zaroori hai — React mein tum DOM ko directly touch nahi karte. Tum sirf batate ho ki "is state ke liye UI aisa dikhna chahiye" aur React khud figure out karta hai ki kya change karna hai. Yeh declarative approach hai jo React ko powerful banata hai.
```

---

## How It Actually Works

### JSX: The Illusion

JSX looks like HTML in JavaScript. It's not. It's a syntax transformation.

```jsx
// What you write (JSX)
const element = <h1 className="greeting">Hello, World!</h1>;
```

```javascript
// What it becomes after Babel compiles it
const element = React.createElement(
  'h1',                          // type
  { className: 'greeting' },     // props
  'Hello, World!'                // children
);
```

```javascript
// What React.createElement returns (a plain object!)
const element = {
  type: 'h1',
  props: {
    className: 'greeting',
    children: 'Hello, World!'
  }
};
```

> **Rule:** JSX is not HTML. It's syntactic sugar for `React.createElement()` calls that return plain JavaScript objects describing your UI.

### Nested Elements

```jsx
// JSX
const element = (
  <div className="container">
    <h1>Title</h1>
    <p>Paragraph</p>
  </div>
);
```

```javascript
// Compiles to
const element = React.createElement(
  'div',
  { className: 'container' },
  React.createElement('h1', null, 'Title'),
  React.createElement('p', null, 'Paragraph')
);
```

```javascript
// Resulting object structure
{
  type: 'div',
  props: {
    className: 'container',
    children: [
      { type: 'h1', props: { children: 'Title' } },
      { type: 'p', props: { children: 'Paragraph' } }
    ]
  }
}
```

This nested object structure is what React calls the **Virtual DOM**.

```narration
JSX dekhne mein HTML lagta hai, but actually yeh sirf React.createElement calls hain. Babel compile karta hai JSX ko plain JavaScript mein. Jo object banta hai — woh hai Virtual DOM element. Yeh samajh lo ki Virtual DOM sirf JavaScript objects ka tree hai, kuch magical nahi hai.
```

### The Virtual DOM Explained

The Virtual DOM is not a shadow copy of the real DOM. It's a lightweight JavaScript representation of what the DOM should look like.

```
┌─────────────────────────────────────────────────────────────┐
│                    THE RECONCILIATION PROCESS                │
│                                                              │
│  1. State Changes                                            │
│         ↓                                                    │
│  2. React creates NEW Virtual DOM tree                       │
│         ↓                                                    │
│  3. React DIFFS old vs new Virtual DOM (reconciliation)      │
│         ↓                                                    │
│  4. React computes MINIMAL set of DOM operations             │
│         ↓                                                    │
│  5. React BATCHES and applies changes to real DOM            │
└─────────────────────────────────────────────────────────────┘
```

Why is this fast?
- JavaScript object comparison is fast
- Real DOM operations are slow (layout, paint, reflow)
- Batching multiple updates into single DOM write

```javascript
// React internally does something like this (simplified)
function updateDOM(oldVDOM, newVDOM) {
  if (oldVDOM.type !== newVDOM.type) {
    // Replace entire node
    replaceNode(oldVDOM, newVDOM);
  } else {
    // Same type - update only changed props
    updateProps(oldVDOM, newVDOM);
    // Recursively diff children
    diffChildren(oldVDOM.children, newVDOM.children);
  }
}
```

### Your First React Code

```jsx
// index.js
import React from 'react';
import ReactDOM from 'react-dom/client';

// Create a React element
const element = <h1>Hello, React!</h1>;

// Get the DOM container
const container = document.getElementById('root');

// Create a root and render
const root = ReactDOM.createRoot(container);
root.render(element);
```

What happens here:
1. `element` is created — a plain JS object via JSX
2. `createRoot` creates a React root attached to a DOM node
3. `render` takes your Virtual DOM, diffs with current state (empty), and updates real DOM

```narration
Dekho, ReactDOM.createRoot aur render — yeh do cheezein hain jo Virtual DOM ko actual DOM mein daalta hai. createRoot basically React ko batata hai ki "is container mein render karna hai". Aur render actual reconciliation trigger karta hai. First render mein kuch diff nahi hota, directly DOM mein inject hota hai.
```

---

## The Rule

> **Rule:** React is declarative — you describe what the UI should look like, not how to change it. UI = f(State).

> **Corollary:** JSX is not template syntax. It's JavaScript with a convenient syntax for creating React elements (plain objects).

> **Corollary:** The Virtual DOM is just a JavaScript object tree. "Virtual" doesn't mean magic — it means "not the real DOM."

---

## Production Story

### The Bug That Killed Performance

A junior developer at a startup built a dashboard with this pattern:

```jsx
// ❌ The problematic code
function Dashboard() {
  const [data, setData] = useState([]);
  
  useEffect(() => {
    fetchData().then(setData);
  }, []);
  
  return (
    <div>
      {data.map(item => (
        // Creating new function on every render!
        <div onclick={() => console.log(item.id)}>
          {item.name}
        </div>
      ))}
    </div>
  );
}
```

Wait, did you catch it? Look again...

```jsx
<div onclick={() => ...}>  // lowercase 'onclick' — this is wrong!
```

In JSX, event handlers use **camelCase**: `onClick`, not `onclick`.

The fix:

```jsx
// ✅ Correct JSX
<div onClick={() => console.log(item.id)}>
  {item.name}
</div>
```

But there was a deeper issue. They also did this:

```jsx
// ❌ HTML attribute names in JSX
<div class="container" for="input-1">
```

JSX uses JavaScript property names, not HTML attributes:

```jsx
// ✅ JSX attribute names (camelCase, JavaScript-style)
<div className="container" htmlFor="input-1">
```

> **Warning:** JSX uses JavaScript naming conventions. `class` → `className`, `for` → `htmlFor`, `onclick` → `onClick`. This trips up everyone coming from HTML. Linters like ESLint with eslint-plugin-react catch these instantly.

```narration
Yeh bahut common mistake hai! HTML mein "class" likhte hain, JSX mein "className" likhna padta hai. Kyun? Kyunki JSX JavaScript hai, aur JavaScript mein "class" ek reserved keyword hai. Similarly "for" bhi reserved hai. Yeh choti choti cheezein bahut time waste karati hain agar dhyan nahi diya toh.
```

---

## Going Deeper

### JSX Expressions and Rules

Inside JSX, you can embed any JavaScript expression using `{}`:

```jsx
const name = 'Rahul';
const element = <h1>Hello, {name}!</h1>;

// Expressions work
const element2 = <h1>2 + 2 = {2 + 2}</h1>;  // "2 + 2 = 4"

// Function calls work
const element3 = <h1>{name.toUpperCase()}</h1>;  // "RAHUL"

// Ternary works
const element4 = <h1>{isLoggedIn ? 'Welcome!' : 'Please log in'}</h1>;
```

But **statements don't work** inside `{}`:

```jsx
// ❌ This breaks - if is a statement, not an expression
const element = <h1>{if (true) { 'Hello' }}</h1>;

// ✅ Use ternary instead
const element = <h1>{true ? 'Hello' : null}</h1>;
```

### Why className and Not class?

```javascript
// In JavaScript, 'class' is a reserved keyword
class MyClass {}  // This is valid JS

// If JSX used 'class', it would conflict:
const element = <div class="foo">  // Parser confusion!

// So React uses 'className' which maps to DOM property
element.className = 'foo';  // This is how you set class in vanilla JS too
```

React chose to align with DOM properties, not HTML attributes. This is consistent — you're writing JavaScript, after all.

### React 17+ JSX Transform

In older React, you needed to import React even if you didn't use it directly:

```jsx
// Old way - React must be in scope for JSX
import React from 'react';

const element = <h1>Hello</h1>;
// Compiles to: React.createElement('h1', null, 'Hello')
```

React 17+ introduced a new JSX transform:

```jsx
// New way - no import needed for JSX
const element = <h1>Hello</h1>;

// Compiles to (simplified):
import { jsx as _jsx } from 'react/jsx-runtime';
const element = _jsx('h1', { children: 'Hello' });
```

The bundler (like Vite or Webpack) handles the import automatically. You only import React when you need hooks or other React APIs.

```narration
Pehle React import karna zaruri tha har file mein jahan JSX use karte the. Ab React 17 ke baad yeh automatically handle hota hai. But samajhna zaroori hai ki yeh sirf syntactic change hai — internally React.createElement hi call hota hai, bass import automatic ho gaya.
```

---

## Connecting the Dots

This lesson establishes the foundation. Here's how it connects forward:

**Next Lesson (Components and Props):** We'll take these JSX elements and compose them into reusable components. You'll see why thinking in components is React's superpower.

**Module 2 (Hooks):** Understanding that `UI = f(State)` is crucial. Hooks are how you manage state — when state changes, React re-runs your function and re-renders.

**Module 3 (Advanced Patterns):** When we discuss performance optimization, you'll understand why — excessive Virtual DOM creation and diffing can be expensive for large trees.

**Module 4 (Production React):** State management solutions like Redux work because React's declarative model means they just need to trigger re-renders with new state.

---

## Practice

### Exercise 1: JSX Compilation

What does this JSX compile to? Write the `React.createElement` equivalent:

```jsx
const card = (
  <div className="card">
    <img src="avatar.png" alt="User" />
    <span>{userName}</span>
  </div>
);
```

<details>
<summary>Answer</summary>

```javascript
const card = React.createElement(
  'div',
  { className: 'card' },
  React.createElement('img', { src: 'avatar.png', alt: 'User' }),
  React.createElement('span', null, userName)
);
```

Note: `userName` is a JavaScript variable, so it stays as-is (not wrapped in quotes). The third argument to the `span`'s createElement is the children — in this case, the value of `userName`.

</details>

### Exercise 2: Fix the Bugs

This code has multiple JSX-related bugs. Find and fix them:

```jsx
function UserProfile() {
  const user = { name: 'Amit', isAdmin: true };
  
  return (
    <div class="profile">
      <label for="username">Name:</label>
      <input id="username" value={user.name} />
      <p onclick={alert('clicked')}>
        {if (user.isAdmin) { 'Admin User' }}
      </p>
    </div>
  );
}
```

<details>
<summary>Answer</summary>

```jsx
function UserProfile() {
  const user = { name: 'Amit', isAdmin: true };
  
  return (
    <div className="profile">                           {/* class → className */}
      <label htmlFor="username">Name:</label>           {/* for → htmlFor */}
      <input id="username" value={user.name} />
      <p onClick={() => alert('clicked')}>              {/* onclick → onClick, wrap in arrow function */}
        {user.isAdmin ? 'Admin User' : null}            {/* if statement → ternary expression */}
      </p>
    </div>
  );
}
```

**Bugs fixed:**
1. `class` → `className` (reserved keyword)
2. `for` → `htmlFor` (reserved keyword)
3. `onclick` → `onClick` (camelCase convention)
4. `alert('clicked')` → `() => alert('clicked')` (handler must be function, not function call)
5. `if` statement → ternary expression (JSX only accepts expressions)

</details>

---

## Study Notes

**Q: Why does React use className instead of class?**
Because JSX is JavaScript, and `class` is a reserved keyword in JavaScript (used for class definitions). React chose to use DOM property names (`className`, `htmlFor`) instead of HTML attribute names to avoid conflicts and stay consistent with JavaScript conventions.

**Q: Is the Virtual DOM actually faster than direct DOM manipulation?**
Not inherently. Direct, surgical DOM updates can be faster. But the Virtual DOM provides a better developer experience — you describe the end state, React figures out the updates. For most applications, the reconciliation overhead is negligible compared to the productivity gains. For extreme performance needs, React provides escape hatches like `useMemo` and `shouldComponentUpdate`.

**Q: Do I need to understand Virtual DOM internals for interviews?**
Yes. Interviewers frequently ask "how does React work under the hood?" You should be able to explain: JSX compiles to createElement, which returns objects forming a Virtual DOM tree. On state change, React creates a new tree, diffs it with the old one (reconciliation), and batches minimal DOM updates. This is React's core value proposition.

---

## Complete

Congratulations! You've built the mental model that makes everything else in React click. You understand that JSX is sugar, Virtual DOM is just objects, and React's job is to efficiently sync your declared UI with the actual DOM.