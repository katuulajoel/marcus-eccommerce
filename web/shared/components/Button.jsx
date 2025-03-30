import React from 'react';

const styles = {
  button: {
    backgroundColor: '#4CAF50',
    border: 'none',
    color: 'white',
    padding: '15px 32px',
    textAlign: 'center',
    textDecoration: 'none',
    display: 'inline-block',
    fontSize: '16px',
    margin: '4px 2px',
    cursor: 'pointer',
    borderRadius: '4px',
  }
};

const Button = ({ children, onClick, className, ...props }) => {
  return (
    <button
      style={styles.button}
      onClick={onClick}
      className={className || ''}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;