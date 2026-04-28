import { useState, useEffect } from 'react';
import { Menu, X } from 'lucide-react';
import { Link } from 'react-router-dom';

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Projects', to: '/project-list' },
  { label: 'Command', to: '/os-command' },
  { label: 'Assistant', to: '/assistant' },
  { label: 'Docs', to: '/documentation' },
];

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 0);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <>
      <nav
        className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
          isScrolled
            ? 'border-b border-white/10 bg-black/70 backdrop-blur-xl'
            : 'bg-gradient-to-b from-black/70 to-transparent'
        }`}
      >
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5 md:px-10">
          <Link to="/" className="font-display text-2xl tracking-[0.18em] text-white transition-colors hover:text-cyan-200">
            Bylexa
          </Link>

          <ul className="hidden items-center gap-8 md:flex">
            {navItems.map((item) => (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className="text-sm uppercase tracking-[0.18em] text-slate-200 transition-colors hover:text-cyan-200"
                >
                  {item.label}
                </Link>
              </li>
            ))}

            <li>
              <Link
                to="/create"
                className="rounded-full border border-cyan-300/60 bg-cyan-400/10 px-5 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-cyan-100 transition hover:bg-cyan-300/20"
              >
                New Project
              </Link>
            </li>
          </ul>

          <button onClick={toggleSidebar} className="text-white transition-colors hover:text-cyan-300 md:hidden" aria-label="Open menu">
            <Menu className="h-6 w-6" />
          </button>
        </div>
      </nav>

      <div
        className={`fixed inset-y-0 left-0 z-[60] w-72 border-r border-white/10 bg-black/95 text-white backdrop-blur-xl transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } transition-transform duration-300 ease-in-out`}
      >
        <div className="flex items-center justify-between border-b border-white/10 p-6">
          <h2 className="font-display text-xl tracking-[0.14em]">Menu</h2>
          <button onClick={toggleSidebar}>
            <X className="h-6 w-6 text-white hover:text-cyan-300" />
          </button>
        </div>
        <ul className="mt-6 space-y-4 px-6">
          {navItems.map((item) => (
            <li key={item.to}>
              <Link
                to={item.to}
                onClick={toggleSidebar}
                className="block border-b border-white/10 py-2 text-sm uppercase tracking-[0.16em] text-slate-100 transition-colors hover:text-cyan-300"
              >
                {item.label}
              </Link>
            </li>
          ))}
          <li>
            <Link
              to="/create"
              onClick={toggleSidebar}
              className="mt-3 inline-flex rounded-full border border-cyan-300/55 bg-cyan-400/10 px-5 py-2 text-xs font-semibold uppercase tracking-[0.18em] text-cyan-100"
            >
              New Project
            </Link>
          </li>
        </ul>
      </div>

      {isSidebarOpen && (
        <div
          onClick={toggleSidebar}
          className="fixed inset-0 z-40 bg-black/65 md:hidden"
        />
      )}
    </>
  );
};

export default Navbar;
