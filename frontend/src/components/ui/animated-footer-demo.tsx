import AnimatedFooter from "./animated-footer";

const AnimatedFooterDemo = () => {
  return (
    <AnimatedFooter
      leftLinks={[
        { href: "/terms", label: "Terms & policies" },
        { href: "/privacy-policy", label: "Privacy policy" },
      ]}
      rightLinks={[
        { href: "/careers", label: "Careers" },
        { href: "/about", label: "About" },
        { href: "/help-center", label: "Help Center" },
        { href: "https://x.com/taher_max_", label: "Twitter" },
        { href: "https://www.instagram.com/taher_max_", label: "Instagram" },
        { href: "https://github.com/tahermaxse", label: "GitHub" },
      ]}
      copyrightText="InfraPilot 2026. All Rights Reserved"
      barCount={23}
    />
  );
};

export { AnimatedFooterDemo };

