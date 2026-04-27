import { useState } from "react";
import { Link } from "react-router-dom";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 w-full bg-white/80 backdrop-blur-md border-b border-[#d2d2d7]">
      <div className="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link
          to="/"
          className="text-xl font-semibold text-[#1d1d1f] tracking-tight"
        >
          InfraPilot
        </Link>

        {/* Desktop links */}
        <div className="hidden md:flex items-center gap-8 text-sm font-medium text-[#1d1d1f]">
          <a
            href="#features"
            className="hover:text-[#0071e3] transition-colors"
          >
            Features
          </a>
          <a
            href="#about"
            className="hover:text-[#0071e3] transition-colors"
          >
            About
          </a>
          <a
            href="#pricing"
            className="hover:text-[#0071e3] transition-colors"
          >
            Pricing
          </a>
          <Link
            to="/login"
            className="px-4 py-1.5 bg-[#0071e3] text-white rounded-full text-sm font-medium hover:bg-[#0077ed] transition-colors"
          >
            Get Started
          </Link>
        </div>

        {/* Mobile menu button */}
        <button
          className="md:hidden text-[#1d1d1f]"
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label="Toggle menu"
        >
          {menuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden px-6 pb-4 flex flex-col gap-3 text-[#1d1d1f]">
          <a
            href="#features"
            onClick={() => setMenuOpen(false)}
            className="py-1"
          >
            Features
          </a>
          <a
            href="#about"
            onClick={() => setMenuOpen(false)}
            className="py-1"
          >
            About
          </a>
          <a
            href="#pricing"
            onClick={() => setMenuOpen(false)}
            className="py-1"
          >
            Pricing
          </a>
          <Link
            to="/login"
            onClick={() => setMenuOpen(false)}
            className="text-[#0071e3] font-medium py-1"
          >
            Get Started
          </Link>
        </div>
      )}
    </nav>
  );
}
