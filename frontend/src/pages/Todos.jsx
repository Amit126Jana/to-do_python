import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  logout,
  getMe,
} from "../api";

export default function Todos() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    async function load() {
      try {
        const [me, todoList] = await Promise.all([getMe(), getTodos()]);
        setEmail(me.email);
        setTodos(todoList);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  async function handleAdd(e) {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      const todo = await createTodo(title.trim());
      setTodos([todo, ...todos]);
      setTitle("");
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleToggle(todo) {
    try {
      const updated = await updateTodo(todo.id, { completed: !todo.completed });
      setTodos(todos.map((t) => (t.id === todo.id ? updated : t)));
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    try {
      await deleteTodo(id);
      setTodos(todos.filter((t) => t.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  function handleLogout() {
    logout();
    navigate("/login");
  }

  if (loading) return <div className="center">Loading...</div>;

  return (
    <div className="todos-page">
      <header className="todos-header">
        <div>
          <h1>My Todos</h1>
          <p className="muted">{email}</p>
        </div>
        <button className="secondary" onClick={handleLogout}>
          Log out
        </button>
      </header>

      {error && <p className="error">{error}</p>}

      <form className="add-form" onSubmit={handleAdd}>
        <input
          type="text"
          placeholder="What needs doing?"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <button type="submit">Add</button>
      </form>

      <ul className="todo-list">
        {todos.length === 0 && <li className="muted">No todos yet.</li>}
        {todos.map((todo) => (
          <li key={todo.id} className={todo.completed ? "completed" : ""}>
            <label>
              <input
                type="checkbox"
                checked={todo.completed}
                onChange={() => handleToggle(todo)}
              />
              <span>{todo.title}</span>
            </label>
            <button className="danger" onClick={() => handleDelete(todo.id)}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
