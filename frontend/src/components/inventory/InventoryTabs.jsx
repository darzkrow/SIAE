import React from 'react';

const InventoryTabs = ({ tabs, activeTab, onTabChange }) => {
    return (
        <div className="card-header p-0 pt-1 border-bottom-0">
            <ul className="nav nav-tabs" role="tablist">
                {tabs.map(tab => (
                    <li key={tab.id} className="nav-item">
                        <a
                            className={`nav-link ${activeTab === tab.id ? 'active' : ''}`}
                            onClick={() => onTabChange(tab.id)}
                            role="button"
                        >
                            <tab.icon size={16} className="mr-2" />
                            {tab.label}
                        </a>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default InventoryTabs;
