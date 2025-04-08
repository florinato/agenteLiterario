import axios from 'axios';
import React, { useCallback, useEffect, useState } from 'react';


// Define the base URL for the backend API
// Ensure the backend is running and accessible from this URL
const API_BASE_URL = 'http://localhost:8000'; // Default FastAPI port

function FileExplorer({ onFileSelect }) { // Add prop to notify parent of file selection
  const [items, setItems] = useState([]);
  const [currentPath, setCurrentPath] = useState(''); // Track current relative path
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchFiles = useCallback(async (relativePath) => {
    setLoading(true);
    setError(null);
    console.log(`Fetching files for path: '${relativePath}'`);
    try {
      const params = relativePath ? { path: relativePath } : {};
      const response = await axios.get(`${API_BASE_URL}/api/files/list`, { params });
      setItems(response.data);
      setCurrentPath(relativePath); // Update current path state
    } catch (err) {
      console.error("Error fetching files:", err);
      setError(`Failed to load list for ${relativePath || 'root'}. Backend running?`);
    } finally {
      setLoading(false);
    }
  }, []); // useCallback avoids recreating function on every render

  useEffect(() => {
    fetchFiles(''); // Fetch root ('historias') on initial mount
  }, [fetchFiles]); // Depend on fetchFiles callback

  const handleItemClick = (item) => {
    if (item.is_directory) {
      fetchFiles(item.path); // Fetch content of the clicked directory
    } else {
      // TODO: Implement file loading in editor
      console.log(`Selected file: ${item.path}`);
      if (onFileSelect) {
        onFileSelect(item.path); // Notify parent component
      }
    }
  };

  const handleGoUp = () => {
    if (!currentPath) return; // Already at root
    // Find the parent path
    const parts = currentPath.split('/').filter(p => p); // Split and remove empty parts
    parts.pop(); // Remove the last part
    const parentPath = parts.join('/');
    fetchFiles(parentPath);
  };

  const renderItems = (itemList) => {
    // Add "Go Up" item if not at the root
    const displayList = currentPath ? [{ name: '.. (Go Up)', path: '..', is_directory: true, is_go_up: true }, ...itemList] : itemList;

    if (!displayList || displayList.length === 0) {
      return <li>No items found.</li>;
    }

    return displayList.map(item => (
      <li
        key={item.path}
        onClick={() => item.is_go_up ? handleGoUp() : handleItemClick(item)}
        title={item.path} // Show full path on hover
        className={item.is_directory ? 'directory-item' : 'file-item'}
      >
        {item.is_go_up ? '⬆️' : (item.is_directory ? '📁' : '📄')} {item.name}
      </li>
    ));
  };

  return (
    <div className="file-explorer">
      <h3>Historias {currentPath && `/ ${currentPath}`}</h3>
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {!loading && !error && (
        <ul>
          {renderItems(items)}
        </ul>
      )}
      {/* TODO: Add buttons for creating files/folders */}
    </div>
  );
}

export default FileExplorer;
