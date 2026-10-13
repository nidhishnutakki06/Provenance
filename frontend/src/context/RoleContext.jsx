import React, { createContext, useContext, useState } from 'react';
import { DEMO_USERS } from '../auth/users';

const RoleContext = createContext();

const STORAGE_KEY = 'provenance_demo_user';

function getStoredUser() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      // Validate that parsed user exists in DEMO_USERS
      const matched = DEMO_USERS.find((u) => u.id === parsed.id && u.role === parsed.role);
      if (matched) {
        return {
          id: matched.id,
          name: matched.name,
          title: matched.title,
          role: matched.role,
        };
      }
    }
  } catch (err) {
    console.error('Failed reading sessionStorage user:', err);
  }
  return null;
}

export function RoleProvider({ children }) {
  const initialUser = getStoredUser();
  const [user, setUser] = useState(initialUser);
  const [role, setRole] = useState(initialUser ? initialUser.role : 'analyst');

  const login = (userId, password) => {
    const account = DEMO_USERS.find((u) => u.id === userId);
    if (account && account.password === password) {
      const safeUser = {
        id: account.id,
        name: account.name,
        title: account.title,
        role: account.role,
      };
      setUser(safeUser);
      setRole(account.role);
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(safeUser));
      } catch (err) {
        console.error('Failed saving user to sessionStorage:', err);
      }
      return true;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    setRole('analyst');
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch (err) {
      console.error('Failed clearing user from sessionStorage:', err);
    }
  };

  return (
    <RoleContext.Provider value={{ role, setRole, user, login, logout }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error('useRole must be used within a RoleProvider');
  }
  return context;
}
