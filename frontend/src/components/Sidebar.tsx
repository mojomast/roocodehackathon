"use client";
import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { FaTachometerAlt, FaCodeBranch, FaTasks, FaUser, FaStore } from 'react-icons/fa';

const navItems = [
  { href: '/dashboard', icon: FaTachometerAlt, label: 'Dashboard' },
  { href: '/repos', icon: FaCodeBranch, label: 'Repositories' },
  { href: '/jobs', icon: FaTasks, label: 'Jobs' },
  { href: '/profile', icon: FaUser, label: 'Profile' },
  { href: '/store', icon: FaStore, label: 'Store' },
];

const Sidebar = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-panel-background text-primary-text p-4 flex flex-col">
      <div className="text-2xl font-bold font-heading mb-10 text-center text-headings">ROOCODE</div>
      <nav className="flex flex-col space-y-2">
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex items-center p-3 rounded-lg transition-all duration-200 ${
              pathname === item.href
                ? 'bg-primary-accent text-white shadow-lg shadow-primary-accent/50'
                : 'hover:bg-borders-dividers'
            }`}
          >
            <item.icon className="mr-4" />
            <span className="font-body">{item.label}</span>
          </Link>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;