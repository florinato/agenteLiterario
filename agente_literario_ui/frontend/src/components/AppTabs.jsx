import React from 'react';

function AppTabs({ openTabs, activeTab, onSelectTab, onCloseTab }) {
  return (
    <div className="tabs" style={{ display: 'flex', borderBottom: '1px solid #ccc' }}>
      {openTabs.map((tab) => (
        <div
          key={tab.path}
          style={{
            padding: '8px 12px',
            cursor: 'pointer',
            backgroundColor: tab.path === activeTab ? '#eee' : 'transparent',
            borderRight: '1px solid #ccc',
            display: 'flex',
            alignItems: 'center'
          }}
        >
          <span 
            onClick={() => onSelectTab(tab.path)}
            style={{ color: tab.path === activeTab ? 'black' : 'white' }}
          >
            {tab.path.split('\\').pop()}
          </span>
          <button
            onClick={() => onCloseTab(tab.path)}
            style={{ marginLeft: 8, cursor: 'pointer', background: 'none', border: 'none' }}
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
}

export default AppTabs;
