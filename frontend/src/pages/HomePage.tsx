import { HeroSection } from "@/components/blocks/hero-section-3";
import AnimatedFooter from "@/components/ui/animated-footer";
import { motion, Variants } from "framer-motion";
import { Shield, Zap, BarChart3, Lock, CheckCircle } from "lucide-react";
import { Link } from "react-router-dom";

const sectionReveal: Variants = {
  hidden: { opacity: 0, filter: "blur(12px)", y: 36 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    y: 0,
    transition: {
      type: "spring",
      bounce: 0.22,
      duration: 1.15,
      staggerChildren: 0.12,
    },
  },
};

const itemReveal: Variants = {
  hidden: { opacity: 0, filter: "blur(10px)", y: 24 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    y: 0,
    transition: { type: "spring", bounce: 0.2, duration: 0.9 },
  },
};

const imageRevealLeft: Variants = {
  hidden: { opacity: 0, filter: "blur(12px)", x: -36 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    x: 0,
    transition: { type: "spring", bounce: 0.18, duration: 1 },
  },
};

const imageRevealRight: Variants = {
  hidden: { opacity: 0, filter: "blur(12px)", x: 36 },
  visible: {
    opacity: 1,
    filter: "blur(0px)",
    x: 0,
    transition: { type: "spring", bounce: 0.18, duration: 1 },
  },
};

const viewportReveal = { once: true, amount: 0.22 };

export default function HomePage() {
  return (
    <div className="min-h-screen bg-white text-[#1d1d1f]">
      <HeroSection />

      {/* Features Section */}
      <section id="features" className="py-24 bg-[#f5f5f7]">
        <motion.div
          className="max-w-5xl mx-auto px-6"
          initial="hidden"
          whileInView="visible"
          viewport={viewportReveal}
          variants={sectionReveal}
        >
          <motion.h2 variants={itemReveal} className="text-3xl md:text-5xl font-semibold text-center mb-4">
            Why InfraPilot?
          </motion.h2>
          <motion.p variants={itemReveal} className="text-[#6e6e73] text-center text-lg mb-16 max-w-2xl mx-auto">
            Detect misconfigurations, predict drift timelines, and auto-generate
            fixes before your infrastructure breaks.
          </motion.p>

          <motion.div variants={sectionReveal} className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <FeatureCard
              icon={<Shield className="w-8 h-8 text-[#0071e3]" />}
              title="Security First"
              desc="AI-driven identification of security risks and anti-patterns in Terraform and Kubernetes."
            />
            <FeatureCard
              icon={<Zap className="w-8 h-8 text-[#0071e3]" />}
              title="Multi-Provider AI"
              desc="Choose from Ollama (local), Gemini (cloud), or Oumi RL for intelligent scoring."
            />
            <FeatureCard
              icon={<BarChart3 className="w-8 h-8 text-[#0071e3]" />}
              title="Timeline Prediction"
              desc="See how issues evolve over time with AI-generated drift progression forecasts."
            />
            <FeatureCard
              icon={<Lock className="w-8 h-8 text-[#0071e3]" />}
              title="Privacy Focused"
              desc="Run analysis entirely offline with local Ollama models—no data leaves your machine."
            />
          </motion.div>
        </motion.div>
      </section>

      {/* About */}
      <section id="about" className="py-24 bg-white">
        <motion.div
          className="max-w-5xl mx-auto px-6"
          initial="hidden"
          whileInView="visible"
          viewport={viewportReveal}
          variants={sectionReveal}
        >
          <div className="flex flex-col md:flex-row gap-12 items-center">
            <motion.div variants={imageRevealLeft} className="flex-1">
              <img
                src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80"
                alt="Team collaboration"
                className="rounded-2xl shadow-xl w-full"
              />
            </motion.div>
            <motion.div variants={sectionReveal} className="flex-1 space-y-6">
              <motion.h2 variants={itemReveal} className="text-3xl md:text-5xl font-semibold mb-4">
                About InfraPilot
              </motion.h2>
              <motion.p variants={itemReveal} className="text-[#6e6e73] text-lg leading-relaxed">
                InfraPilot was born from a simple observation: infrastructure
                drift is the silent killer of cloud reliability. We watched teams
                spend hours in war rooms tracing misconfigurations that could
                have been caught in minutes.
              </motion.p>
              <motion.p variants={itemReveal} className="text-[#6e6e73] text-lg leading-relaxed">
                Our mission is to give DevOps and platform engineers an
                AI-powered co-pilot that continuously scans Terraform and
                Kubernetes manifests, predicts drift before it happens, and
                suggests precise fixes—so you ship faster and sleep better.
              </motion.p>
              <motion.div variants={itemReveal} className="grid grid-cols-2 gap-6 pt-4">
                <div>
                  <div className="text-3xl font-semibold text-[#0071e3]">10k+</div>
                  <div className="text-sm text-[#6e6e73]">Analyses run</div>
                </div>
                <div>
                  <div className="text-3xl font-semibold text-[#0071e3]">99.9%</div>
                  <div className="text-sm text-[#6e6e73]">Uptime protected</div>
                </div>
              </motion.div>
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 bg-[#f5f5f7]">
        <motion.div
          className="max-w-5xl mx-auto px-6"
          initial="hidden"
          whileInView="visible"
          viewport={viewportReveal}
          variants={sectionReveal}
        >
          <motion.h2 variants={itemReveal} className="text-3xl md:text-5xl font-semibold text-center mb-16">
            How it works
          </motion.h2>
          <div className="flex flex-col md:flex-row gap-12 items-center">
            <motion.div variants={sectionReveal} className="flex-1 space-y-8">
              <Step
                number="01"
                title="Paste your code"
                desc="Upload Terraform or Kubernetes manifests directly in the dashboard."
              />
              <Step
                number="02"
                title="Select an AI model"
                desc="Pick from local Ollama models or cloud providers like Gemini."
              />
              <Step
                number="03"
                title="Get insights"
                desc="Receive a drift score, timeline, and actionable fix suggestions instantly."
              />
            </motion.div>
            <motion.div variants={imageRevealRight} className="flex-1">
              <img
                src="https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80"
                alt="Dashboard preview"
                className="rounded-2xl shadow-xl w-full"
              />
            </motion.div>
          </div>
        </motion.div>
      </section>

      {/* Pricing teaser */}
      <section id="pricing" className="py-24 bg-[#f5f5f7]">
        <motion.div
          className="max-w-3xl mx-auto px-6 text-center"
          initial="hidden"
          whileInView="visible"
          viewport={viewportReveal}
          variants={sectionReveal}
        >
          <motion.h2 variants={itemReveal} className="text-3xl md:text-5xl font-semibold mb-4">
            Simple pricing
          </motion.h2>
          <motion.p variants={itemReveal} className="text-[#6e6e73] text-lg mb-12">
            Start free. Scale as your infrastructure grows.
          </motion.p>
          <motion.div variants={itemReveal} className="bg-white rounded-[18px] p-8 shadow-sm border border-[#d2d2d7]">
            <h3 className="text-2xl font-semibold mb-2">Free tier</h3>
            <p className="text-[#6e6e73] mb-6">
              Everything you need to get started.
            </p>
            <div className="text-4xl font-semibold mb-6">
              $0
              <span className="text-lg font-normal text-[#6e6e73]">/mo</span>
            </div>
            <ul className="text-left space-y-3 mb-8 text-[#1d1d1f]">
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-[#0071e3]" /> Up to 50
                analyses / month
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-[#0071e3]" /> Local
                Ollama support
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-[#0071e3]" /> Rule-engine
                fallback
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle size={16} className="text-[#0071e3]" /> Email
                summaries
              </li>
            </ul>
            <div className="text-center">
              <Link
                to="/login"
                className="inline-block px-8 py-3 bg-[#0071e3] text-white rounded-full text-lg font-medium hover:bg-[#0077ed] transition-colors"
              >
                Get Started
              </Link>
            </div>
          </motion.div>
        </motion.div>
      </section>

      <AnimatedFooter
        leftLinks={[
          { href: "#", label: "Terms & policies" },
          { href: "#", label: "Privacy policy" },
        ]}
        rightLinks={[
          { href: "#", label: "Careers" },
          { href: "#", label: "About" },
          { href: "#", label: "Help Center" },
          { href: "https://x.com", label: "Twitter" },
          { href: "https://instagram.com", label: "Instagram" },
          { href: "https://github.com", label: "GitHub" },
        ]}
        copyrightText="InfraPilot 2026. All Rights Reserved"
        barCount={23}
      />
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  desc,
}: {
  icon: React.ReactNode;
  title: string;
  desc: string;
}) {
  return (
    <motion.div variants={itemReveal} className="bg-white rounded-[18px] p-6 border border-[#d2d2d7] hover:shadow-md transition-shadow">
      <div className="mb-4">{icon}</div>
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-[#6e6e73] text-sm leading-relaxed">{desc}</p>
    </motion.div>
  );
}

function Step({
  number,
  title,
  desc,
}: {
  number: string;
  title: string;
  desc: string;
}) {
  return (
    <motion.div variants={itemReveal} className="flex gap-4">
      <div className="text-2xl font-semibold text-[#0071e3]">{number}</div>
      <div>
        <h4 className="text-lg font-semibold mb-1">{title}</h4>
        <p className="text-[#6e6e73] text-sm">{desc}</p>
      </div>
    </motion.div>
  );
}
