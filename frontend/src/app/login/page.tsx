// frontend/src/app/login/page.tsx
import React, { Suspense } from 'react';
import Login from './Login';

const LoginPage = () => {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Login />
    </Suspense>
  );
};

export default LoginPage;