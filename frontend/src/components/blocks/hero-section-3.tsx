'use client'
import React from 'react'
import { Mail, SendHorizonal, Menu, X } from 'lucide-react'
import { AnimatePresence, motion } from 'framer-motion'
import { Button } from '@/components/ui/button'
import { AnimatedGroup } from '@/components/ui/animated-group'
import { cn } from '@/lib/utils'
import { Link } from 'react-router-dom'
import { InfiniteSlider } from '@/components/ui/infinite-slider'
import { ProgressiveBlur } from '@/components/ui/progressive-blur'

const transitionVariants = {
    item: {
        hidden: { opacity: 0, filter: 'blur(12px)', y: 12 },
        visible: { opacity: 1, filter: 'blur(0px)', y: 0, transition: { type: 'spring' as const, bounce: 0.3, duration: 1.5 } },
    },
}

export function HeroSection() {
    return (
        <>
            <HeroHeader />
            <main className="overflow-hidden">
                <section>
                    <div className="relative mx-auto max-w-6xl px-6 pt-32 lg:pb-16 lg:pt-48">
                        <div className="relative z-10 mx-auto max-w-4xl text-center">
                            <AnimatedGroup variants={{ container: { visible: { transition: { staggerChildren: 0.05, delayChildren: 0.75 } } }, ...transitionVariants }}>
                                <h1 className="text-balance text-4xl font-medium sm:text-5xl md:text-6xl text-[#1d1d1f] dark:text-white">AI-Powered Infrastructure Drift Detection</h1>
                                <p className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-[#6e6e73] dark:text-zinc-300">Detect misconfigurations, predict drift timelines, and auto-generate fixes before your infrastructure breaks. Powered by multi-provider AI.</p>
                                <div className="mt-12 mx-auto max-w-sm">
                                    <div className="bg-white dark:bg-zinc-950/80 relative grid grid-cols-[1fr_auto] items-center rounded-[1rem] border border-[#d2d2d7] dark:border-white/10 p-1 shadow shadow-zinc-950/5 dark:shadow-black/30 has-[input:focus]:ring-2 has-[input:focus]:ring-[#0071e3]/30">
                                        <Mail className="pointer-events-none absolute inset-y-0 left-4 my-auto size-4 text-[#86868b] dark:text-zinc-500" />
                                        <input placeholder="Enter your email" className="h-11 min-w-0 w-full bg-transparent pl-12 pr-3 focus:outline-none text-[#1d1d1f] dark:text-white placeholder:text-[#86868b] dark:placeholder:text-zinc-500" type="email" />
                                        <div>
                                            <Button asChild size="sm" className="h-10 rounded-[0.7rem] bg-[#0071e3] px-5 text-white shadow-sm shadow-blue-600/20 hover:bg-[#0077ed]">
                                                <Link to="/login"><span className="hidden md:block">Get Started</span><SendHorizonal className="relative mx-auto size-5 md:hidden" strokeWidth={2} /></Link>
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                                <div aria-hidden className="relative mx-auto mt-32 max-w-2xl to-transparent to-55% text-left">
                                    <div className="bg-white dark:bg-zinc-950 border-[#d2d2d7]/50 dark:border-white/10 absolute inset-0 mx-auto w-80 -translate-x-3 -translate-y-12 rounded-[2rem] border p-2 [mask-image:linear-gradient(to_bottom,#000_50%,transparent_90%)] sm:-translate-x-6">
                                        <div className="relative h-96 overflow-hidden rounded-[1.5rem] border p-2 pb-12 before:absolute before:inset-0 before:bg-[repeating-linear-gradient(-45deg,var(--border),var(--border)_1px,transparent_1px,transparent_6px)] before:opacity-50"></div>
                                    </div>
                                    <div className="bg-[#f5f5f7] dark:bg-zinc-900 border-[#d2d2d7]/50 dark:border-white/10 mx-auto w-80 translate-x-4 rounded-[2rem] border p-2 backdrop-blur-3xl [mask-image:linear-gradient(to_bottom,#000_50%,transparent_90%)] sm:translate-x-8">
                                        <div className="bg-white dark:bg-zinc-950 space-y-2 overflow-hidden rounded-[1.5rem] border border-[#d2d2d7] dark:border-white/10 p-2 shadow-xl dark:shadow-black/40">
                                            <AppComponent />
                                            <div className="bg-[#f5f5f7] dark:bg-white/5 rounded-[1rem] p-4 pb-16"></div>
                                        </div>
                                    </div>
                                    <div className="absolute inset-0 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] mix-blend-overlay [background-size:16px_16px] [mask-image:radial-gradient(ellipse_50%_50%_at_50%_50%,#000_70%,transparent_100%)] opacity-5" />
                                </div>
                            </AnimatedGroup>
                        </div>
                    </div>
                </section>
                <LogoCloud />
            </main>
        </>
    )
}

const AppComponent = () => {
    return (
        <div className="relative space-y-3 rounded-[1rem] bg-white/5 p-4">
            <div className="flex items-center gap-1.5 text-orange-500">
                <svg className="size-5" xmlns="http://www.w3.org/2000/svg" width="1em" height="1em" viewBox="0 0 32 32">
                    <g fill="none">
                        <path fill="#ff6723" d="M26 19.34c0 6.1-5.05 11.005-11.15 10.641c-6.269-.374-10.56-6.403-9.752-12.705c.489-3.833 2.286-7.12 4.242-9.67c.34-.445.689 3.136 1.038 2.742c.35-.405 3.594-6.019 4.722-7.991a.694.694 0 0 1 1.028-.213C18.394 3.854 26 10.277 26 19.34" />
                        <path fill="#ffb02e" d="M23 21.851c0 4.042-3.519 7.291-7.799 7.144c-4.62-.156-7.788-4.384-7.11-8.739C9.07 14.012 15.48 10 15.48 10S23 14.707 23 21.851" />
                    </g>
                </svg>
                <div className="text-sm font-medium text-[#1d1d1f] dark:text-white">InfraPilot</div>
            </div>
            <div className="space-y-3">
                <div className="text-[#1d1d1f] dark:text-white border-b border-[#d2d2d7]/50 dark:border-white/10 pb-3 text-sm font-medium">Your infrastructure is 23% healthier than last month.</div>
                <div className="space-y-3">
                    <div className="space-y-1">
                        <div className="space-x-1">
                            <span className="text-[#1d1d1f] dark:text-white align-baseline text-xl font-medium">98.2%</span>
                            <span className="text-[#6e6e73] dark:text-zinc-400 text-xs">Uptime</span>
                        </div>
                        <div className="flex h-5 items-center rounded bg-gradient-to-l from-emerald-400 to-indigo-600 px-2 text-xs text-white">2024</div>
                    </div>
                    <div className="space-y-1">
                        <div className="space-x-1">
                            <span className="text-[#1d1d1f] dark:text-white align-baseline text-xl font-medium">12</span>
                            <span className="text-[#6e6e73] dark:text-zinc-400 text-xs">Issues Fixed</span>
                        </div>
                        <div className="text-[#1d1d1f] dark:text-zinc-300 bg-[#f5f5f7] dark:bg-white/10 flex h-5 w-2/3 items-center rounded px-2 text-xs">2023</div>
                    </div>
                </div>
            </div>
        </div>
    )
}

const menuItems = [
    { name: 'Features', href: '#features' },
    { name: 'How it Works', href: '#how-it-works' },
    { name: 'Pricing', href: '#pricing' },
    { name: 'About', href: '#about' },
]

const makeLogoSrc = (label: string, initials: string, accent: string) => {
    const svg = `
        <svg xmlns="http://www.w3.org/2000/svg" width="190" height="44" viewBox="0 0 190 44">
            <rect width="190" height="44" rx="12" fill="white"/>
            <rect x="1" y="1" width="188" height="42" rx="11" fill="none" stroke="#E5E7EB"/>
            <rect x="14" y="10" width="24" height="24" rx="7" fill="${accent}"/>
            <path d="M20 27L26 15L32 27" fill="none" stroke="white" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="26" cy="27" r="2.3" fill="white"/>
            <text x="50" y="27" fill="#1D1D1F" font-family="Inter, Arial, sans-serif" font-size="15" font-weight="700">${label}</text>
            <text x="16" y="27" fill="white" font-family="Inter, Arial, sans-serif" font-size="8" font-weight="800" opacity=".2">${initials}</text>
        </svg>
    `

    return `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`
}

const customerLogos = [
    { label: 'DriftOps', initials: 'DO', accent: '#0071E3' },
    { label: 'KubeGrid', initials: 'KG', accent: '#635BFF' },
    { label: 'TerraGuard', initials: 'TG', accent: '#10B981' },
    { label: 'CloudForge', initials: 'CF', accent: '#F97316' },
    { label: 'OpsLens', initials: 'OL', accent: '#0EA5E9' },
    { label: 'StackPulse', initials: 'SP', accent: '#8B5CF6' },
    { label: 'VaultRun', initials: 'VR', accent: '#111827' },
    { label: 'NodeWorks', initials: 'NW', accent: '#22C55E' },
].map((logo) => ({
    ...logo,
    src: makeLogoSrc(logo.label, logo.initials, logo.accent),
}))

const HeroHeader = () => {
    const [menuState, setMenuState] = React.useState(false)
    const [isScrolled, setIsScrolled] = React.useState(false)

    React.useEffect(() => {
        const handleScroll = () => { setIsScrolled(window.scrollY > 50) }
        window.addEventListener('scroll', handleScroll)
        return () => window.removeEventListener('scroll', handleScroll)
    }, [])

    return (
        <header>
            <motion.nav
                className="fixed z-20 w-full px-2"
                initial={{ opacity: 0, filter: 'blur(14px)', y: -18 }}
                animate={{ opacity: 1, filter: 'blur(0px)', y: 0 }}
                transition={{ type: 'spring', bounce: 0.18, duration: 1.1, delay: 0.15 }}
            >
                <motion.div
                    layout
                    transition={{ layout: { type: 'spring', bounce: 0.18, duration: 0.75 } }}
                    className={cn(
                        'mx-auto mt-2 px-5 lg:px-8',
                        isScrolled
                            ? 'max-w-4xl bg-white/80 dark:bg-zinc-950/80 rounded-2xl border border-[#d2d2d7] dark:border-white/10 shadow-lg shadow-zinc-950/5 dark:shadow-black/30 backdrop-blur-lg lg:px-5'
                            : 'max-w-5xl'
                    )}
                >
                    <div className="relative flex flex-wrap items-center justify-between gap-6 py-2.5 lg:gap-0 lg:py-3">
                        <motion.div layout className="flex w-full justify-between lg:w-auto">
                            <motion.div whileHover={{ y: -1 }} whileTap={{ scale: 0.98 }}>
                                <Link to="/" aria-label="home" className="flex items-center space-x-2">
                                    <Logo />
                                </Link>
                            </motion.div>
                            <motion.button
                                onClick={() => setMenuState(!menuState)}
                                aria-label={menuState == true ? 'Close Menu' : 'Open Menu'}
                                className="relative z-20 -m-2.5 -mr-4 block cursor-pointer p-2.5 lg:hidden"
                                whileTap={{ scale: 0.92 }}
                            >
                                <AnimatePresence initial={false} mode="wait">
                                    {menuState ? (
                                        <motion.span
                                            key="close"
                                            className="block"
                                            initial={{ opacity: 0, rotate: -90, scale: 0.72 }}
                                            animate={{ opacity: 1, rotate: 0, scale: 1 }}
                                            exit={{ opacity: 0, rotate: 90, scale: 0.72 }}
                                            transition={{ type: 'spring', bounce: 0.25, duration: 0.35 }}
                                        >
                                            <X className="m-auto size-6" />
                                        </motion.span>
                                    ) : (
                                        <motion.span
                                            key="menu"
                                            className="block"
                                            initial={{ opacity: 0, rotate: 90, scale: 0.72 }}
                                            animate={{ opacity: 1, rotate: 0, scale: 1 }}
                                            exit={{ opacity: 0, rotate: -90, scale: 0.72 }}
                                            transition={{ type: 'spring', bounce: 0.25, duration: 0.35 }}
                                        >
                                            <Menu className="m-auto size-6" />
                                        </motion.span>
                                    )}
                                </AnimatePresence>
                            </motion.button>
                        </motion.div>
                        <div className="absolute inset-0 m-auto hidden size-fit lg:block">
                            <motion.ul
                                className="flex gap-8 text-sm"
                                initial="hidden"
                                animate="visible"
                                variants={{
                                    hidden: {},
                                    visible: { transition: { staggerChildren: 0.08, delayChildren: 0.35 } },
                                }}
                            >
                                {menuItems.map((item, index) => (
                                    <motion.li
                                        key={index}
                                        variants={{
                                            hidden: { opacity: 0, filter: 'blur(8px)', y: -8 },
                                            visible: { opacity: 1, filter: 'blur(0px)', y: 0, transition: { type: 'spring', bounce: 0.24, duration: 0.65 } },
                                        }}
                                        whileHover={{ y: -2 }}
                                    >
                                        <a href={item.href} className="group/link relative block py-2 text-[#6e6e73] dark:text-zinc-300 duration-200 hover:text-[#1d1d1f] dark:hover:text-white">
                                            <span>{item.name}</span>
                                            <span className="absolute inset-x-0 -bottom-0.5 mx-auto h-px w-0 bg-[#0071e3] transition-all duration-300 group-hover/link:w-full" />
                                        </a>
                                    </motion.li>
                                ))}
                            </motion.ul>
                        </div>
                        <motion.div layout className="hidden w-fit items-center justify-end gap-3 lg:flex">
                            <AnimatePresence initial={false} mode="popLayout">
                                {!isScrolled && (
                                    <motion.div
                                        key="login"
                                        initial={{ opacity: 0, filter: 'blur(8px)', x: 12 }}
                                        animate={{ opacity: 1, filter: 'blur(0px)', x: 0 }}
                                        exit={{ opacity: 0, filter: 'blur(8px)', x: 12 }}
                                        transition={{ type: 'spring', bounce: 0.2, duration: 0.45 }}
                                        whileHover={{ y: -1 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <Button asChild variant="outline" size="sm">
                                            <Link to="/login"><span>Login</span></Link>
                                        </Button>
                                    </motion.div>
                                )}
                                {isScrolled && (
                                    <motion.div
                                        key="get-started"
                                        initial={{ opacity: 0, filter: 'blur(8px)', x: 12 }}
                                        animate={{ opacity: 1, filter: 'blur(0px)', x: 0 }}
                                        exit={{ opacity: 0, filter: 'blur(8px)', x: 12 }}
                                        transition={{ type: 'spring', bounce: 0.2, duration: 0.45 }}
                                        whileHover={{ y: -1 }}
                                        whileTap={{ scale: 0.98 }}
                                    >
                                        <Button asChild size="sm" className="bg-[#0071e3] text-white hover:bg-[#0077ed]">
                                            <Link to="/login"><span>Get Started</span></Link>
                                        </Button>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    </div>
                    <AnimatePresence>
                        {menuState && (
                            <motion.div
                                className="mb-4 origin-top overflow-hidden rounded-3xl border border-[#d2d2d7] dark:border-white/10 bg-white dark:bg-zinc-950 p-6 shadow-2xl shadow-zinc-300/20 dark:shadow-black/40 will-change-transform lg:hidden"
                                initial={{ opacity: 0, scaleY: 0.96, y: -8 }}
                                animate={{ opacity: 1, scaleY: 1, y: 0 }}
                                exit={{ opacity: 0, scaleY: 0.96, y: -8 }}
                                transition={{ type: 'spring', bounce: 0.12, duration: 0.38 }}
                            >
                                <motion.ul
                                    className="space-y-5 text-base"
                                    initial="hidden"
                                    animate="visible"
                                    variants={{
                                        hidden: {},
                                        visible: { transition: { staggerChildren: 0.07, delayChildren: 0.06 } },
                                    }}
                                >
                                    {menuItems.map((item, index) => (
                                        <motion.li
                                            key={index}
                                            variants={{
                                                hidden: { opacity: 0, x: -10 },
                                                visible: { opacity: 1, x: 0, transition: { type: 'spring', bounce: 0.18, duration: 0.36 } },
                                            }}
                                        >
                                            <a
                                                href={item.href}
                                                onClick={() => setMenuState(false)}
                                                className="block text-[#6e6e73] dark:text-zinc-300 duration-150 hover:text-[#1d1d1f] dark:hover:text-white"
                                            >
                                                <span>{item.name}</span>
                                            </a>
                                        </motion.li>
                                    ))}
                                </motion.ul>
                                <motion.div
                                    className="mt-6 flex w-full flex-col space-y-3 sm:flex-row sm:gap-3 sm:space-y-0"
                                    initial={{ opacity: 0, y: 10 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: 0.16, type: 'spring', bounce: 0.2, duration: 0.45 }}
                                >
                                    <Button asChild variant="outline" size="sm">
                                        <Link to="/login"><span>Login</span></Link>
                                    </Button>
                                    <Button asChild size="sm" className="bg-[#0071e3] text-white hover:bg-[#0077ed]">
                                        <Link to="/login"><span>Get Started</span></Link>
                                    </Button>
                                </motion.div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </motion.div>
            </motion.nav>
        </header>
    )
}

const LogoCloud = () => {
    return (
        <section className="bg-white dark:bg-[#07080c] pb-16 md:pb-32">
            <div className="group relative m-auto max-w-6xl px-6">
                <div className="flex flex-col items-center md:flex-row">
                    <div className="inline md:max-w-44 md:border-r md:border-[#d2d2d7] md:pr-6">
                        <p className="text-end text-sm text-[#6e6e73] dark:text-zinc-400">Powering the best teams</p>
                    </div>
                    <div className="relative py-6 md:w-[calc(100%-11rem)]">
                        <InfiniteSlider durationOnHover={20} duration={40} gap={112}>
                            {customerLogos.map((logo) => (
                                <div className="flex" key={logo.label}>
                                    <img className="mx-auto h-11 w-[190px] object-contain opacity-80 transition-opacity group-hover:opacity-100" src={logo.src} alt={`${logo.label} logo`} height="44" width="190" />
                                </div>
                            ))}
                        </InfiniteSlider>
                        <div className="bg-gradient-to-r from-white absolute inset-y-0 left-0 w-20"></div>
                        <div className="bg-gradient-to-l from-white absolute inset-y-0 right-0 w-20"></div>
                        <ProgressiveBlur className="pointer-events-none absolute left-0 top-0 h-full w-20" direction="left" blurIntensity={1} />
                        <ProgressiveBlur className="pointer-events-none absolute right-0 top-0 h-full w-20" direction="right" blurIntensity={1} />
                    </div>
                </div>
            </div>
        </section>
    )
}

const Logo = ({ className }: { className?: string }) => {
    return (
        <span className={cn('text-xl font-semibold tracking-tight text-[#1d1d1f] dark:text-white', className)}>InfraPilot</span>
    )
}
