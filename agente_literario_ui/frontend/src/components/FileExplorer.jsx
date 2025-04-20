import axios from 'axios';
import React, { useCallback, useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function FileExplorer({ onFileSelect }) {
  const [items, setItems] = useState([]);
  const [currentPath, setCurrentPath] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchFiles = useCallback(async (relativePath) => {
    setLoading(true);
    setError(null);
    try {
      const params = relativePath ? { path: relativePath } : {};
      const response = await axios.get(`${API_BASE_URL}/api/files/list`, { params });
      setItems(response.data);
      setCurrentPath(relativePath);
    } catch (err) {
      setError(`Error al cargar ${relativePath || 'root'}.`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchFiles('');
  }, [fetchFiles]);

  const handleItemClick = (item) => {
    if (item.is_directory) {
      fetchFiles(item.path);
    } else {
      if (onFileSelect) {
        onFileSelect(item.path);
      }
    }
  };

  const handleGoUp = () => {
    if (!currentPath) return;
    const parts = currentPath.split('/').filter(p => p);
    parts.pop();
    const parentPath = parts.join('/');
    fetchFiles(parentPath);
  };

  const handleCreate = async (type) => {
    const name = window.prompt(`Nombre del nuevo ${type === 'file' ? 'archivo' : 'directorio'}:`);
    if (!name) return;
    const fullPath = currentPath ? `${currentPath}/${name}` : name;

    try {
      await axios.post(`${API_BASE_URL}/api/files/create`, {
        path: fullPath,
        type,
      });
      fetchFiles(currentPath);
    } catch (err) {
      alert('Error al crear el ítem.');
    }
  };

  const handleRename = async (item) => {
    const newName = window.prompt(`Nuevo nombre para '${item.name}':`);
    if (!newName) return;

    try {
      await axios.post(`${API_BASE_URL}/api/files/rename`, {
        oldPath: item.path,
        newPath: currentPath ? `${currentPath}/${newName}` : newName,
      });
      fetchFiles(currentPath);
    } catch (err) {
      alert('Error al renombrar el ítem.');
    }
  };

  const handleDelete = async (item) => {
    const confirmed = window.confirm(`¿Eliminar '${item.name}'?`);
    if (!confirmed) return;

    try {
      await axios.delete(`${API_BASE_URL}/api/files/delete`, {
        params: { path: item.path },
      });
      fetchFiles(currentPath);
    } catch (err) {
      alert(`Error al borrar el ítem: ${err}`);
    }
  };

  const renderItems = (itemList) => {
    const displayList = currentPath
      ? [{ name: '.. (Subir)', path: '..', is_directory: true, is_go_up: true }, ...itemList]
      : itemList;

    if (!displayList || displayList.length === 0) {
      return <li style={{ padding: '0.5rem' }}>📭 Carpeta vacía.</li>;
    }

    return displayList.map((item) => (
      <li
        key={item.path}
        onClick={() => item.is_go_up ? handleGoUp() : handleItemClick(item)}
        className="file-explorer-item"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '0.5rem',
          borderBottom: '1px solid #555',
          cursor: 'pointer',
          color: 'var(--text-color)',
        }}
      >
        <span>
          {item.is_go_up
            ? '⬆️'
            : item.is_directory
            ? '📁'
            : '📄'}{' '}
          {item.name}
        </span>
        {!item.is_go_up && (
          <div>
            <button
              style={{
                background: '#555',
                border: 'none',
                color: 'var(--text-color)',
                cursor: 'pointer',
                fontSize: '1rem',
                marginRight: '0.5rem',
                padding: '0.25rem',
              }}
              onClick={(e) => {
                e.stopPropagation();
                handleRename(item);
              }}
              title="Renombrar"
            >
              ✏️
            </button>
            <button
              style={{
                background: '#555',
                border: 'none',
                color: 'var(--text-color)',
                cursor: 'pointer',
                fontSize: '1rem',
                padding: '0.25rem',
              }}
              onClick={(e) => {
                e.stopPropagation();
                handleDelete(item);
              }}
              title="Borrar"
            >
              🗑️
            </button>
          </div>
        )}
      </li>
    ));
  };

  return (
    <div style={{ border: '1px solid #555', padding: '1rem', background: 'var(--sidebar-bg-color)', color: 'var(--text-color)' }}>
      <h3>📚 Explorador de archivos {currentPath && `/ ${currentPath}`}</h3>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
        <button title="Crear archivo" onClick={() => handleCreate('file')} style={{ padding: '0.5rem 1rem', background: '#555', color: 'var(--text-color)', border: 'none' }}>
          ➕
        </button>
        <button title="Crear carpeta" onClick={() => handleCreate('directory')} style={{ padding: '0.5rem 1rem', background: '#555', color: 'var(--text-color)', border: 'none' }}>
          📂
        </button>
      </div>

      {loading && <p style={{color: 'var(--text-color)'}}>⏳ Cargando archivos...</p>}
      {error && <p style={{ color: 'var(--text-color)' }}>{error}</p>}
      {!loading && !error && <ul style={{ listStyle: 'none', padding: 0 }}>{renderItems(items)}</ul>}
    </div>
  );
}

export default FileExplorer;
