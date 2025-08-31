'use client';

import React, { useState, createContext, useContext, ReactNode } from 'react';

type TabsContextType = {
  activeTab: number;
  setActiveTab: (index: number) => void;
};

const TabsContext = createContext<TabsContextType | undefined>(undefined);

export function Tabs({ children }: { children: ReactNode }) {
  const [activeTab, setActiveTab] = useState(0);

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className="tab-container">{children}</div>
    </TabsContext.Provider>
  );
}

export function TabList({ children }: { children: ReactNode }) {
  return <div className="tab-list">{children}</div>;
}

export function Tab({ index, children }: { index: number; children: ReactNode }) {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('Tab must be used within a Tabs component');
  }
  const { activeTab, setActiveTab } = context;

  return (
    <button
      className={`tab-button ${activeTab === index ? 'active' : ''}`}
      onClick={() => setActiveTab(index)}
    >
      {children}
    </button>
  );
}

export function TabPanels({ children }: { children: ReactNode }) {
  return <div className="tab-panels">{children}</div>;
}

export function TabPanel({ index, children }: { index: number; children: ReactNode }) {
  const context = useContext(TabsContext);
  if (!context) {
    throw new Error('TabPanel must be used within a Tabs component');
  }
  const { activeTab } = context;

  return activeTab === index ? <div className="tab-panel">{children}</div> : null;
}