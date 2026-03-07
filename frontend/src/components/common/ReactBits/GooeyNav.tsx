import React, { useRef, useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export interface GooeyNavItem {
    label: string;
    href: string;
    icon?: any;
}

export interface GooeyNavProps {
    items: GooeyNavItem[];
    animationTime?: number;
    particleCount?: number;
    particleDistances?: [number, number];
    particleR?: number;
    timeVariance?: number;
    colors?: number[];
    initialActiveIndex?: number;
}

const GooeyNav: React.FC<GooeyNavProps> = ({
    items,
    animationTime = 600,
    particleCount = 15,
    particleDistances = [90, 10],
    particleR = 100,
    timeVariance = 300,
    colors = [1, 2, 3, 1, 2, 3, 1, 4],
    initialActiveIndex = 0
}) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const navRef = useRef<HTMLUListElement>(null);
    const filterRef = useRef<HTMLSpanElement>(null);
    const textRef = useRef<HTMLSpanElement>(null);

    const navigate = useNavigate();
    const location = useLocation();

    const currentPath = location.pathname + location.hash;
    const initialIndex = items.findIndex(item => item.href === currentPath);
    const [activeIndex, setActiveIndex] = useState<number>(initialIndex >= 0 ? initialIndex : initialActiveIndex);

    useEffect(() => {
        const newPath = location.pathname + location.hash;
        const newIndex = items.findIndex(item => item.href === newPath);
        if (newIndex >= 0 && newIndex !== activeIndex) {
            setActiveIndex(newIndex);
        }
    }, [location.pathname, location.hash, items]);

    useEffect(() => {
        // Also re-render if activeIndex changes and the ref needs positioning
        if (navRef.current && containerRef.current) {
            const activeLi = navRef.current.querySelectorAll('li')[activeIndex] as HTMLElement;
            if (activeLi) {
                updateEffectPosition(activeLi);
                textRef.current?.classList.add('active');
            }
        }
    }, [activeIndex]);

    const noise = (n = 1) => n / 2 - Math.random() * n;
    const getXY = (distance: number, pointIndex: number, totalPoints: number): [number, number] => {
        const angle = ((360 + noise(8)) / totalPoints) * pointIndex * (Math.PI / 180);
        return [distance * Math.cos(angle), distance * Math.sin(angle)];
    };

    const createParticle = (i: number, t: number, d: [number, number], r: number) => {
        const rotate = noise(r / 10);
        return {
            start: getXY(d[0], particleCount - i, particleCount),
            end: getXY(d[1] + noise(7), particleCount - i, particleCount),
            time: t,
            scale: 1 + noise(0.2),
            color: colors[Math.floor(Math.random() * colors.length)],
            rotate: rotate > 0 ? (rotate + r / 20) * 10 : (rotate - r / 20) * 10
        };
    };

    const makeParticles = (element: HTMLElement) => {
        const d: [number, number] = particleDistances;
        const r = particleR;
        const bubbleTime = animationTime * 2 + timeVariance;
        element.style.setProperty('--time', `${bubbleTime}ms`);
        for (let i = 0; i < particleCount; i++) {
            const t = animationTime * 2 + noise(timeVariance * 2);
            const p = createParticle(i, t, d, r);
            element.classList.remove('active');
            setTimeout(() => {
                const particle = document.createElement('span');
                const point = document.createElement('span');
                particle.classList.add('particle');
                particle.style.setProperty('--start-x', `${p.start[0]}px`);
                particle.style.setProperty('--start-y', `${p.start[1]}px`);
                particle.style.setProperty('--end-x', `${p.end[0]}px`);
                particle.style.setProperty('--end-y', `${p.end[1]}px`);
                particle.style.setProperty('--time', `${p.time}ms`);
                particle.style.setProperty('--scale', `${p.scale}`);

                // Use brand colors for standard light background
                const brandColors = ["#4f46e5", "#6366f1", "#818cf8", "#4338ca", "#3730a3"];
                particle.style.setProperty('--color', brandColors[p.color % brandColors.length]);

                particle.style.setProperty('--rotate', `${p.rotate}deg`);
                point.classList.add('point');
                particle.appendChild(point);
                element.appendChild(particle);
                requestAnimationFrame(() => {
                    element.classList.add('active');
                });
                setTimeout(() => {
                    try {
                        element.removeChild(particle);
                    } catch { }
                }, t);
            }, 30);
        }
    };

    const updateEffectPosition = (element: HTMLElement) => {
        if (!containerRef.current || !filterRef.current || !textRef.current) return;
        const containerRect = containerRef.current.getBoundingClientRect();
        const pos = element.getBoundingClientRect();
        const styles = {
            left: `${pos.x - containerRect.x}px`,
            top: `${pos.y - containerRect.y}px`,
            width: `${pos.width}px`,
            height: `${pos.height}px`
        };
        Object.assign(filterRef.current.style, styles);
        Object.assign(textRef.current.style, styles);
        textRef.current.innerHTML = element.innerHTML;
    };

    const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, index: number) => {
        e.preventDefault();
        const liEl = e.currentTarget.parentElement;
        if (!liEl) return;

        navigate(items[index].href);

        if (activeIndex === index) return;
        setActiveIndex(index);
        updateEffectPosition(liEl);

        if (filterRef.current) {
            const particles = filterRef.current.querySelectorAll('.particle');
            particles.forEach(p => filterRef.current!.removeChild(p));
        }
        if (textRef.current) {
            textRef.current.classList.remove('active');
            void textRef.current.offsetWidth;
            textRef.current.classList.add('active');
        }
        if (filterRef.current) {
            makeParticles(filterRef.current);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLAnchorElement>, index: number) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            const liEl = e.currentTarget.parentElement;
            if (liEl) {
                handleClick(
                    {
                        currentTarget: e.currentTarget,
                        preventDefault: () => { }
                    } as React.MouseEvent<HTMLAnchorElement>,
                    index
                );
            }
        }
    };

    useEffect(() => {
        if (!navRef.current || !containerRef.current) return;
        const activeLi = navRef.current.querySelectorAll('li')[activeIndex] as HTMLElement;
        if (activeLi) {
            updateEffectPosition(activeLi);
            textRef.current?.classList.add('active');
        }
        const resizeObserver = new ResizeObserver(() => {
            const currentActiveLi = navRef.current?.querySelectorAll('li')[activeIndex] as HTMLElement;
            if (currentActiveLi) {
                updateEffectPosition(currentActiveLi);
            }
        });
        resizeObserver.observe(containerRef.current);
        return () => resizeObserver.disconnect();
    }, [activeIndex]);

    return (
        <>
            <style>
                {`
          :root {
            --linear-ease: linear(0, 0.068, 0.19 2.7%, 0.804 8.1%, 1.037, 1.199 13.2%, 1.245, 1.27 15.8%, 1.274, 1.272 17.4%, 1.249 19.1%, 0.996 28%, 0.949, 0.928 33.3%, 0.926, 0.933 36.8%, 1.001 45.6%, 1.013, 1.019 50.8%, 1.018 54.4%, 1 63.1%, 0.995 68%, 1.001 85%, 1);
          }
          .effect {
            position: absolute;
            opacity: 1;
            pointer-events: none;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1;
          }
          .effect.text {
            color: #64748b; /* text-slate-500 */
            transition: color 0.3s ease;
            white-space: nowrap;
          }
          .effect.text.active {
            color: #ffffff; /* text-white */
          }
          .effect.filter {
            filter: blur(5px) contrast(80) blur(0);
            mix-blend-mode: normal;
          }
          .effect.filter::before {
            content: "";
            position: absolute;
            inset: -40px;
            z-index: -2;
            background: #ffffff;
          }
          .effect.filter::after {
            content: "";
            position: absolute;
            inset: 0;
            background: #4f46e5; /* indigo-600 active bubble */
            transform: scale(0);
            opacity: 0;
            z-index: -1;
            border-radius: 9999px;
          }
          .effect.active::after {
            animation: pill 0.3s ease both;
          }
          @keyframes pill {
            to {
              transform: scale(1);
              opacity: 1;
            }
          }
          .particle,
          .point {
            display: block;
            opacity: 0;
            width: 20px;
            height: 20px;
            border-radius: 9999px;
            transform-origin: center;
          }
          .particle {
            --time: 5s;
            position: absolute;
            top: calc(50% - 10px);
            left: calc(50% - 10px);
            animation: particle calc(var(--time)) ease 1 -350ms;
          }
          .point {
            background: var(--color);
            opacity: 1;
            animation: point calc(var(--time)) ease 1 -350ms;
          }
          @keyframes particle {
            0% {
              transform: rotate(0deg) translate(calc(var(--start-x)), calc(var(--start-y)));
              opacity: 1;
              animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
            }
            70% {
              transform: rotate(calc(var(--rotate) * 0.5)) translate(calc(var(--end-x) * 1.2), calc(var(--end-y) * 1.2));
              opacity: 1;
              animation-timing-function: ease;
            }
            85% {
              transform: rotate(calc(var(--rotate) * 0.66)) translate(calc(var(--end-x)), calc(var(--end-y)));
              opacity: 1;
            }
            100% {
              transform: rotate(calc(var(--rotate) * 1.2)) translate(calc(var(--end-x) * 0.5), calc(var(--end-y) * 0.5));
              opacity: 1;
            }
          }
          @keyframes point {
            0% {
              transform: scale(0);
              opacity: 0;
              animation-timing-function: cubic-bezier(0.55, 0, 1, 0.45);
            }
            25% {
              transform: scale(calc(var(--scale) * 0.25));
            }
            38% {
              opacity: 1;
            }
            65% {
              transform: scale(var(--scale));
              opacity: 1;
              animation-timing-function: ease;
            }
            85% {
              transform: scale(var(--scale));
              opacity: 1;
            }
            100% {
              transform: scale(0);
              opacity: 0;
            }
          }
          li.active a {
            color: transparent;
            text-shadow: none;
          }
          li.active::after {
            opacity: 1;
            transform: scale(1);
          }
          li::after {
            content: "";
            position: absolute;
            inset: 0;
            border-radius: 9999px;
            background: transparent;
            opacity: 0;
            transform: scale(0);
            transition: all 0.3s ease;
            z-index: -1;
          }
        `}
            </style>
            <div className="relative w-full" ref={containerRef}>
                <nav className="flex relative items-center w-full" style={{ transform: 'translate3d(0,0,0.01px)' }}>
                    <ul
                        ref={navRef}
                        className="flex gap-2 xl:gap-4 list-none p-0 mx-2 relative z-[3] items-center"
                        style={{ color: '#64748b' }}
                    >
                        {items.map((item, index) => (
                            <li
                                key={index}
                                className={`rounded-full shrink-0 relative cursor-pointer px-1 transition-[color] duration-300 ease text-slate-500 hover:text-indigo-600 ${activeIndex === index ? 'active' : ''
                                    }`}
                            >
                                <a
                                    href={item.href}
                                    onClick={e => handleClick(e, index)}
                                    onKeyDown={e => handleKeyDown(e, index)}
                                    className="outline-none py-2 px-2 xl:py-2.5 xl:px-4 inline-flex items-center text-sm font-semibold whitespace-nowrap"
                                >
                                    <span className="w-[18px] h-[18px] mr-1.5 flex items-center justify-center shrink-0">
                                        <item.icon className="w-full h-full" />
                                    </span>
                                    {item.label}
                                </a>
                            </li>
                        ))}
                    </ul>

                    <span className="effect filter" ref={filterRef} />
                    <span className="effect text" ref={textRef} />
                </nav>
            </div>
        </>
    );
};

export default GooeyNav;
