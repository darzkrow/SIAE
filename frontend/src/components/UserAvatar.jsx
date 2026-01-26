import React from 'react';

/**
 * Componente UserAvatar
 * Genera un avatar circular con las iniciales del usuario
 */
const UserAvatar = ({ 
  username = 'Usuario', 
  size = 32, 
  backgroundColor = '#6366F1',
  textColor = 'white',
  className = '',
  style = {}
}) => {
  // Obtener las iniciales del usuario
  const getInitials = (name) => {
    if (!name) return 'U';
    const names = name.trim().split(' ');
    if (names.length === 1) {
      return names[0].charAt(0).toUpperCase();
    }
    return (names[0].charAt(0) + names[names.length - 1].charAt(0)).toUpperCase();
  };

  const avatarStyle = {
    width: `${size}px`,
    height: `${size}px`,
    backgroundColor,
    color: textColor,
    borderRadius: '50%',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: `${Math.max(size * 0.4, 12)}px`,
    fontWeight: 'bold',
    flexShrink: 0,
    ...style
  };

  return (
    <div 
      className={`user-avatar ${className}`}
      style={avatarStyle}
      title={username}
    >
      {getInitials(username)}
    </div>
  );
};

export default UserAvatar;