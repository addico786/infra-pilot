'use client'
import React from 'react'
import { Mail, SendHorizonal, Menu, X } from 'lucide-react'
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
                                <h1 className="text-balance text-4xl font-medium sm:text-5xl md:text-6xl text-[#1d1d1f]">AI-Powered Infrastructure Drift Detection</h1>
                                <p className="mx-auto mt-6 max-w-2xl text-pretty text-lg text-[#6e6e73]">Detect misconfigurations, predict drift timelines, and auto-generate fixes before your infrastructure breaks. Powered by multi-provider AI.</p>
                                <div className="mt-12 mx-auto max-w-sm">
                                    <div className="bg-white relative grid grid-cols-[1fr_auto] pr-1.5 items-center rounded-[1rem] border border-[#d2d2d7] shadow shadow-zinc-950/5 has-[input:focus]:ring-2 has-[input:focus]:ring-[#0071e3]/30 lg:pr-0">
                                        <Mail className="pointer-events-none absolute inset-y-0 left-4 my-auto size-4 text-[#86868b]" />
                                        <input placeholder="Enter your email" className="h-12 w-full bg-transparent pl-12 focus:outline-none text-[#1d1d1f] placeholder:text-[#86868b]" type="email" />
                                        <div className="md:pr-1.5 lg:pr-0">
                                            <Button asChild size="sm" className="rounded-[0.5rem] bg-[#0071e3] hover:bg-[#0077ed] text-white">
                                                <Link to="/dashboard"><span className="hidden md:block">Get Started</span><SendHorizonal className="relative mx-auto size-5 md:hidden" strokeWidth={2} /></Link>
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                                <div aria-hidden className="relative mx-auto mt-32 max-w-2xl to-transparent to-55% text-left">
                                    <div className="bg-white border-[#d2d2d7]/50 absolute inset-0 mx-auto w-80 -translate-x-3 -translate-y-12 rounded-[2rem] border p-2 [mask-image:linear-gradient(to_bottom,#000_50%,transparent_90%)] sm:-translate-x-6">
                                        <div className="relative h-96 overflow-hidden rounded-[1.5rem] border p-2 pb-12 before:absolute before:inset-0 before:bg-[repeating-linear-gradient(-45deg,var(--border),var(--border)_1px,transparent_1px,transparent_6px)] before:opacity-50"></div>
                                    </div>
                                    <div className="bg-[#f5f5f7] border-[#d2d2d7]/50 mx-auto w-80 translate-x-4 rounded-[2rem] border p-2 backdrop-blur-3xl [mask-image:linear-gradient(to_bottom,#000_50%,transparent_90%)] sm:translate-x-8">
                                        <div className="bg-white space-y-2 overflow-hidden rounded-[1.5rem] border p-2 shadow-xl">
                                            <AppComponent />
                                            <div className="bg-[#f5f5f7] rounded-[1rem] p-4 pb-16"></div>
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
                <div className="text-sm font-medium text-[#1d1d1f]">InfraPilot</div>
            </div>
            <div className="space-y-3">
                <div className="text-[#1d1d1f] border-b border-[#d2d2d7]/50 pb-3 text-sm font-medium">Your infrastructure is 23% healthier than last month.</div>
                <div className="space-y-3">
                    <div className="space-y-1">
                        <div className="space-x-1">
                            <span className="text-[#1d1d1f] align-baseline text-xl font-medium">98.2%</span>
                            <span className="text-[#6e6e73] text-xs">Uptime</span>
                        </div>
                        <div className="flex h-5 items-center rounded bg-gradient-to-l from-emerald-400 to-indigo-600 px-2 text-xs text-white">2024</div>
                    </div>
                    <div className="space-y-1">
                        <div className="space-x-1">
                            <span className="text-[#1d1d1f] align-baseline text-xl font-medium">12</span>
                            <span className="text-[#6e6e73] text-xs">Issues Fixed</span>
                        </div>
                        <div className="text-[#1d1d1f] bg-[#f5f5f7] flex h-5 w-2/3 items-center rounded px-2 text-xs">2023</div>
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
            <nav data-state={menuState && 'active'} className="fixed group z-20 w-full px-2">
                <div className={cn('mx-auto mt-2 max-w-6xl px-6 transition-all duration-300 lg:px-12', isScrolled && 'bg-white/80 max-w-4xl rounded-2xl border border-[#d2d2d7] backdrop-blur-lg lg:px-5')}>
                    <div className="relative flex flex-wrap items-center justify-between gap-6 py-3 lg:gap-0 lg:py-4">
                        <div className="flex w-full justify-between lg:w-auto">
                            <Link to="/" aria-label="home" className="flex items-center space-x-2">
                                <Logo />
                            </Link>
                            <button onClick={() => setMenuState(!menuState)} aria-label={menuState == true ? 'Close Menu' : 'Open Menu'} className="relative z-20 -m-2.5 -mr-4 block cursor-pointer p-2.5 lg:hidden">
                                <Menu className="group-data-[state=active]:rotate-180 group-data-[state=active]:scale-0 group-data-[state=active]:opacity-0 m-auto size-6 duration-200" />
                                <X className="group-data-[state=active]:rotate-0 group-data-[state=active]:scale-100 group-data-[state=active]:opacity-100 absolute inset-0 m-auto size-6 -rotate-180 scale-0 opacity-0 duration-200" />
                            </button>
                        </div>
                        <div className="absolute inset-0 m-auto hidden size-fit lg:block">
                            <ul className="flex gap-8 text-sm">
                                {menuItems.map((item, index) => (
                                    <li key={index}>
                                        <a href={item.href} className="text-[#6e6e73] hover:text-[#1d1d1f] block duration-150"><span>{item.name}</span></a>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="bg-white group-data-[state=active]:block lg:group-data-[state=active]:flex mb-6 hidden w-full flex-wrap items-center justify-end space-y-8 rounded-3xl border border-[#d2d2d7] p-6 shadow-2xl shadow-zinc-300/20 md:flex-nowrap lg:m-0 lg:flex lg:w-fit lg:gap-6 lg:space-y-0 lg:border-transparent lg:bg-transparent lg:p-0 lg:shadow-none">
                            <div className="lg:hidden">
                                <ul className="space-y-6 text-base">
                                    {menuItems.map((item, index) => (
                                        <li key={index}>
                                            <a href={item.href} className="text-[#6e6e73] hover:text-[#1d1d1f] block duration-150"><span>{item.name}</span></a>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                            <div className="flex w-full flex-col space-y-3 sm:flex-row sm:gap-3 sm:space-y-0 md:w-fit">
                                <Button asChild variant="outline" size="sm" className={cn(isScrolled && 'lg:hidden')}>
                                    <Link to="/dashboard"><span>Login</span></Link>
                                </Button>
                                <Button asChild size="sm" className={cn(isScrolled ? 'lg:inline-flex' : 'hidden', 'bg-[#0071e3] hover:bg-[#0077ed] text-white')}>
                                    <Link to="/dashboard"><span>Get Started</span></Link>
                                </Button>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>
        </header>
    )
}

const LogoCloud = () => {
    return (
        <section className="bg-white pb-16 md:pb-32">
            <div className="group relative m-auto max-w-6xl px-6">
                <div className="flex flex-col items-center md:flex-row">
                    <div className="inline md:max-w-44 md:border-r md:border-[#d2d2d7] md:pr-6">
                        <p className="text-end text-sm text-[#6e6e73]">Powering the best teams</p>
                    </div>
                    <div className="relative py-6 md:w-[calc(100%-11rem)]">
                        <InfiniteSlider durationOnHover={20} duration={40} gap={112}>
                            <div className="flex"><img className="mx-auto h-5 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/nvidia.svg" alt="Nvidia Logo" height="20" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-4 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/column.svg" alt="Column Logo" height="16" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-4 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/github.svg" alt="GitHub Logo" height="16" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-5 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/nike.svg" alt="Nike Logo" height="20" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-5 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/lemonsqueezy.svg" alt="Lemon Squeezy Logo" height="20" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-4 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/laravel.svg" alt="Laravel Logo" height="16" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-7 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/lilly.svg" alt="Lilly Logo" height="28" width="auto" /></div>
                            <div className="flex"><img className="mx-auto h-6 w-fit dark:invert" src="https://html.tailus.io/blocks/customers/openai.svg" alt="OpenAI Logo" height="24" width="auto" /></div>
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
        <span className={cn('text-xl font-semibold tracking-tight text-[#1d1d1f]', className)}>InfraPilot</span>
    )
}
