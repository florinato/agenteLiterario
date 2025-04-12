// Paso 1: instala la librería con:
// npm install react-resizable-panels

import axios from 'axios';
import React, { useCallback, useRef, useState } from 'react';
import {
  Panel,
  PanelGroup,
  PanelResizeHandle,
} from 'react-resizable-panels';
import './App.css';
import EditorCanvas from './components/EditorCanvas';
import ErrorBoundary from './components/ErrorBoundary';
import FileExplorer from './components/FileExplorer';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [selectedFilePath, setSelectedFilePath] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [isLoadingContent, setIsLoadingContent] = useState(false);
  const [contentError, setContentError] = useState(null);
  const [agentResponse, setAgentResponse] = useState('');
  const [isAgentLoading, setIsAgentLoading] = useState(false);
  const [agentError, setAgentError] = useState(null);
  const [promptInput, setPromptInput] = useState('');
  const [conversation, setConversation] = useState([]);
  const promptInputRef = useRef(null);

  const handleFileSelect = useCallback(async (filePath) => {
    setSelectedFilePath(filePath);
    setIsLoadingContent(true);
    setContentError(null);
    setAgentResponse('');
    setFileContent('');

    try {
      const response = await axios.get(`${API_BASE_URL}/api/files/read`, {
        params: { path: filePath },
      });
      setFileContent(response.data.content);
    } catch (err) {
      setContentError(`Failed to load content for ${filePath}.`);
    } finally {
      setIsLoadingContent(false);
    }
  }, []);

  const handleFileSave = useCallback(async (filePath, content) => {
    setIsAgentLoading(true);
    setAgentError(null);
    try {
      await axios.post(`${API_BASE_URL}/api/files/save`, {
        path: filePath,
        content,
      });
      setFileContent(content);
    } catch (err) {
      setAgentError('Failed to save file.');
    } finally {
      setIsAgentLoading(false);
    }
  }, []);

  const handleAgentPrompt = useCallback(async () => {
    if (!promptInput.trim()) {
      setAgentError('Please enter a prompt before sending.');
      return;
    }
    setIsAgentLoading(true);
    setAgentError(null);
    setAgentResponse('');
    setConversation((prev) => [...prev, { role: 'user', content: promptInput }]);

    try {
      const response = await axios.post(`${API_BASE_URL}/api/agent/command`, {
        prompt: promptInput,
        file_path: selectedFilePath || '',
      });
      const agentResponse = response.data.response;
      setAgentResponse(agentResponse);
      setConversation((prev) => [...prev, { role: 'agent', content: agentResponse }]);
    } catch (err) {
      setAgentError('Failed to run agent command.');
      setConversation([]);
    } finally {
      setIsAgentLoading(false);
    }
  }, [promptInput, selectedFilePath]);

  const handleInputChange = (event) => {
    setPromptInput(event.target.value);
  };

  return (
    <ErrorBoundary>
      <PanelGroup direction="horizontal">
        <Panel defaultSize={20} minSize={15}>
          <div className="sidebar">
            <FileExplorer onFileSelect={handleFileSelect} />
          </div>
        </Panel>
        <PanelResizeHandle className="resize-handle-horizontal" />
        <Panel minSize={60}>
          <PanelGroup direction="vertical">
            <Panel defaultSize={65} minSize={40}>
              <div className="editor-placeholder">
                <h2>Editor: {selectedFilePath || 'No file selected'}</h2>
                {isLoadingContent && <p>Loading content...</p>}
                {contentError && <p style={{ color: 'red' }}>{contentError}</p>}
                {!isLoadingContent && !contentError && (
                  <EditorCanvas
                    filePath={selectedFilePath}
                    content={fileContent}
                    onSave={handleFileSave}
                  />
                )}
              </div>
            </Panel>
            <PanelResizeHandle className="resize-handle-vertical" />
            <Panel minSize={20}>
              <div className="response-placeholder">
                <h3>Agent Response:</h3>
                {isAgentLoading && <p>Loading...</p>}
                {agentError && <p style={{ color: 'red' }}>{agentError}</p>}
                {conversation.map((msg, index) => (
                  <div key={index} style={{ marginBottom: '10px' }}>
                    <strong>{msg.role === 'user' ? 'User:' : 'Agent:'}</strong>
                    <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace' }}>
                      {msg.content}
                    </pre>
                  </div>
                ))}
                <div className="prompt-placeholder">
                  <input
                    type="text"
                    placeholder="Enter prompt for agent..."
                    value={promptInput}
                    onChange={handleInputChange}
                    ref={promptInputRef}
                  />
                  <button onClick={handleAgentPrompt}>Send</button>
                </div>
              </div>
            </Panel>
          </PanelGroup>
        </Panel>
      </PanelGroup>
    </ErrorBoundary>
  );
}

export default App;
