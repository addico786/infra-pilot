"use client";

import React, { useEffect, useRef, useState } from "react";

interface LinkItem {
  href: string;
  label: string;
}

interface FooterProps {
  leftLinks: LinkItem[];
  rightLinks: LinkItem[];
  copyrightText: string;
  barCount?: number;
}

const AnimatedFooter: React.FC<FooterProps> = ({
  leftLinks,
  rightLinks,
  copyrightText,
  barCount = 23,
}) => {
  const waveRefs = useRef<(HTMLDivElement | null)[]>([]);
  const footerRef = useRef<HTMLDivElement | null>(null);
  const [isVisible, setIsVisible] = useState(false);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        setIsVisible(entry.isIntersecting);
      },
      { threshold: 0.2 }
    );

    if (footerRef.current) {
      observer.observe(footerRef.current);
    }

    return () => {
      if (footerRef.current) {
        observer.unobserve(footerRef.current);
      }
    };
  }, []);

  useEffect(() => {
    let t = 0;

    const animateWave = () => {
      const waveElements = waveRefs.current;
      let offset = 0;

      waveElements.forEach((element, index) => {
        if (element) {
          offset += Math.max(0, 20 * Math.sin((t + index) * 0.3));
          element.style.transform = `translateY(${index + offset}px)`;
        }
      });

      t += 0.1;
      animationFrameRef.current = requestAnimationFrame(animateWave);
    };

    if (isVisible) {
      animateWave();
    } else if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
    };
  }, [isVisible]);

  return (
    <footer ref={footerRef} className="animated-footer-root">
      <div className="animated-footer-inner">
        <div className="animated-footer-brand">
          <div className="animated-footer-mark" aria-hidden="true">
            <span />
          </div>
          <div>
            <p className="animated-footer-kicker">InfraPilot</p>
            <h2 className="animated-footer-title">
              Keep drift, risk, and surprise outages out of your cloud.
            </h2>
          </div>
          <p className="animated-footer-copy">
            Analyze Terraform and Kubernetes, forecast infrastructure drift,
            and generate fixes before small configuration issues become
            production problems.
          </p>
          <button
            className="animated-footer-cta"
            onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
          >
            Back to top
          </button>
        </div>

        <div className="animated-footer-nav">
          <div className="animated-footer-link-group">
            <p className="animated-footer-link-heading">Product</p>
            <ul className="animated-footer-links">
              {rightLinks.slice(0, 3).map((link, index) => (
                <li key={index}>
                  <a href={link.href} className="animated-footer-link">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div className="animated-footer-link-group">
            <p className="animated-footer-link-heading">Connect</p>
            <ul className="animated-footer-links">
              {rightLinks.slice(3).map((link, index) => (
                <li key={index}>
                  <a href={link.href} className="animated-footer-link">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div className="animated-footer-link-group">
            <p className="animated-footer-link-heading">Legal</p>
            <ul className="animated-footer-links">
              {leftLinks.map((link, index) => (
                <li key={index}>
                  <a href={link.href} className="animated-footer-link">
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <div className="animated-footer-bottom">
        <p className="animated-footer-copyright">{copyrightText}</p>
        <p className="animated-footer-status">AI drift detection for modern infrastructure.</p>
      </div>

      <div aria-hidden="true" className="animated-footer-wave">
        <div>
          {Array.from({ length: barCount }).map((_, index) => (
            <div
              key={index}
              ref={(el) => {
                waveRefs.current[index] = el;
              }}
              className="wave-segment"
              style={{
                height: `${index + 1}px`,
                transition: "transform 0.1s ease",
                willChange: "transform",
              }}
            />
          ))}
        </div>
      </div>
    </footer>
  );
};

export default AnimatedFooter;
