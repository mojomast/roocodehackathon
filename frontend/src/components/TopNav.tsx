'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import React from 'react';

const navLinks = [
  { name: 'Dashboard', href: '/dashboard' },
  { name: 'Repositories', href: '/repos' },
  { name: 'Jobs', href: '/jobs' },
  { name: 'Profile', href: '/profile' },
  { name: 'Store', href: '/store' },
  { name: 'ROOCODE', href: '/' },
];

export function TopNav() {
  const pathname = usePathname();

  return (
    <nav className="tab-container">
      <div className="tab-list">
        {navLinks.map((link) => {
          const isActive = pathname === link.href;
          return (
            <Link
              href={link.href}
              key={link.name}
              className={`tab-button ${isActive ? 'active' : ''}`}
            >
              {link.name}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}