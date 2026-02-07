import React from 'react';
import { Package, Plus } from 'lucide-react';

const InventoryHeader = ({ showForm, editingId, onToggleForm, currentTabLabel, isAdmin }) => {
    return (
        <div className="content-header">
            <div className="container-fluid">
                <div className="row mb-2">
                    <div className="col-sm-6">
                        <h1 className="m-0">
                            <Package className="mr-2" size={24} />
                            Catálogo de Artículos
                        </h1>
                    </div>
                    <div className="col-sm-6">
                        <div className="float-sm-right">
                            {isAdmin && (
                                <button
                                    onClick={onToggleForm}
                                    className={`btn ${showForm && !editingId ? 'btn-secondary' : 'btn-primary'}`}
                                >
                                    {showForm && !editingId ? (
                                        <>Cancelar</>
                                    ) : (
                                        <>
                                            <Plus size={16} className="mr-2" />
                                            Nuevo {currentTabLabel?.slice(0, -1)}
                                        </>
                                    )}
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default InventoryHeader;
