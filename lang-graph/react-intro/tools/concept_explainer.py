from langchain_core.tools import tool

@tool
def explain_react_concept(concept: str) -> str:
    """解释React概念
    
    Args:
        concept: 要解释的React概念，如"JSX", "组件", "状态", "属性"等
    
    Returns:
        concept的详细解释
    """
    
    explanations = {
        "jsx": """
JSX (JavaScript XML) 是React的核心语法扩展：

**什么是JSX？**
- JSX是一种JavaScript的语法扩展，允许在JavaScript中编写类似HTML的代码
- 它将HTML标记和JavaScript逻辑结合在一起
- JSX最终会被编译成JavaScript函数调用

**基本语法：**
```jsx
const element = <h1>Hello, World!</h1>;
```

**JSX表达式：**
```jsx
const name = "张三";
const element = <h1>Hello, {name}!</h1>;
```

**JSX属性：**
```jsx
const element = <div className="container" id="main">内容</div>;
```

**注意事项：**
- 使用className而不是class
- 使用camelCase命名属性
- 必须有一个根元素或使用Fragment
        """,
        
        "组件": """
React组件是构建UI的基本单位：

**函数组件（推荐）：**
```jsx
function Welcome(props) {
    return <h1>Hello, {props.name}!</h1>;
}
```

**箭头函数组件：**
```jsx
const Welcome = (props) => {
    return <h1>Hello, {props.name}!</h1>;
};
```

**组件使用：**
```jsx
function App() {
    return (
        <div>
            <Welcome name="张三" />
            <Welcome name="李四" />
        </div>
    );
}
```

**组件规则：**
- 组件名必须以大写字母开头
- 组件必须返回单个JSX元素
- 组件可以接收props参数
        """,
        
        "状态": """
State（状态）是React组件的核心概念：

**useState Hook：**
```jsx
import { useState } from 'react';

function Counter() {
    const [count, setCount] = useState(0);
    
    return (
        <div>
            <p>计数: {count}</p>
            <button onClick={() => setCount(count + 1)}>
                增加
            </button>
        </div>
    );
}
```

**状态更新：**
```jsx
// 直接更新
setCount(count + 1);

// 函数式更新
setCount(prevCount => prevCount + 1);

// 对象状态更新
const [user, setUser] = useState({name: '', age: 0});
setUser(prevUser => ({...prevUser, name: '张三'}));
```

**状态规则：**
- 状态是不可变的，必须通过setState更新
- 状态更新可能是异步的
- 状态更新会触发组件重新渲染
        """,
        
        "属性": """
Props（属性）是组件间传递数据的方式：

**基本使用：**
```jsx
// 父组件
function App() {
    return <UserCard name="张三" age={25} isActive={true} />;
}

// 子组件
function UserCard(props) {
    return (
        <div>
            <h2>{props.name}</h2>
            <p>年龄: {props.age}</p>
            <p>状态: {props.isActive ? '活跃' : '非活跃'}</p>
        </div>
    );
}
```

**解构Props：**
```jsx
function UserCard({ name, age, isActive }) {
    return (
        <div>
            <h2>{name}</h2>
            <p>年龄: {age}</p>
            <p>状态: {isActive ? '活跃' : '非活跃'}</p>
        </div>
    );
}
```

**默认Props：**
```jsx
function UserCard({ name = "匿名用户", age = 0, isActive = false }) {
    // 组件逻辑
}
```

**Props规则：**
- Props是只读的，不能修改
- Props可以是任何JavaScript值
- Props从父组件传递给子组件
        """,
        
        "事件": """
React中的事件处理：

**基本事件处理：**
```jsx
function Button() {
    const handleClick = () => {
        alert('按钮被点击了！');
    };
    
    return <button onClick={handleClick}>点击我</button>;
}
```

**事件对象：**
```jsx
function Input() {
    const handleChange = (event) => {
        console.log('输入值:', event.target.value);
    };
    
    return <input onChange={handleChange} />;
}
```

**传递参数：**
```jsx
function TodoList() {
    const handleDelete = (id) => {
        console.log('删除项目:', id);
    };
    
    return (
        <div>
            <button onClick={() => handleDelete(1)}>删除项目1</button>
            <button onClick={() => handleDelete(2)}>删除项目2</button>
        </div>
    );
}
```

**常用事件：**
- onClick: 点击事件
- onChange: 输入变化事件
- onSubmit: 表单提交事件
- onMouseOver: 鼠标悬停事件
        """,
        
        "生命周期": """
React组件生命周期（使用Hooks）：

**useEffect Hook：**
```jsx
import { useState, useEffect } from 'react';

function UserProfile() {
    const [user, setUser] = useState(null);
    
    // 组件挂载时执行
    useEffect(() => {
        fetchUser().then(setUser);
    }, []); // 空依赖数组表示只在挂载时执行
    
    // 监听状态变化
    useEffect(() => {
        console.log('用户状态更新:', user);
    }, [user]); // 当user变化时执行
    
    // 清理函数
    useEffect(() => {
        const timer = setInterval(() => {
            console.log('定时器运行');
        }, 1000);
        
        return () => clearInterval(timer); // 组件卸载时清理
    }, []);
    
    return user ? <div>{user.name}</div> : <div>加载中...</div>;
}
```

**生命周期阶段：**
1. 挂载（Mounting）：组件被创建并插入DOM
2. 更新（Updating）：组件重新渲染
3. 卸载（Unmounting）：组件从DOM中移除
        """
    }
    
    concept_lower = concept.lower()
    if concept_lower in explanations:
        return explanations[concept_lower]
    
    # 如果没有找到具体概念，返回通用说明
    return f"""
概念 "{concept}" 的说明：

这是一个React概念，但我暂时没有详细的解释。建议您查看以下资源：

**推荐学习资源：**
1. React官方文档: https://react.dev/
2. React中文文档: https://react.docschina.org/
3. MDN Web文档: https://developer.mozilla.org/

**可用的概念解释：**
- JSX: JavaScript XML语法
- 组件: React的基本构建块
- 状态: 组件的内部数据
- 属性: 组件间传递的数据
- 事件: 用户交互处理
- 生命周期: 组件的生命周期管理

请尝试询问这些具体概念！
    """ 