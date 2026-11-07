import {ReactNode,useLayoutEffect,useRef} from 'react';

/** Package 1 presentation policy; never slices data or changes calculations. */
export const DATA_PAGE_SIZE = 15;

export default function DataViewport({children,label,className=''}:{children:ReactNode;label:string;className?:string}){
  const element=useRef<HTMLDivElement>(null);
  useLayoutEffect(()=>{
    const node=element.current;if(!node)return;
    let frame:number|undefined;
    const measure=()=>{
      const rows=Array.from(node.querySelectorAll<HTMLElement>('tbody > tr, [data-viewport-row]'))
        .filter(row=>row.closest('.data-viewport')===node).slice(0,DATA_PAGE_SIZE);
      if(!rows.length||!node.clientWidth)return;
      // Actual row heights include multiline evidence. Nested lists measure themselves.
      const height=Math.ceil(rows[rows.length-1].getBoundingClientRect().bottom-node.getBoundingClientRect().top+node.scrollTop+2);
      const value=height+'px';if(height>0&&node.style.getPropertyValue('--data-viewport-height')!==value)node.style.setProperty('--data-viewport-height',value);
    };
    const schedule=()=>{if(frame!==undefined)cancelAnimationFrame(frame);frame=requestAnimationFrame(measure);};
    const observer=typeof ResizeObserver==='undefined'?null:new ResizeObserver(schedule);
    observer?.observe(node);if(node.firstElementChild)observer?.observe(node.firstElementChild);
    window.addEventListener('resize',schedule);measure();
    return()=>{observer?.disconnect();window.removeEventListener('resize',schedule);if(frame!==undefined)cancelAnimationFrame(frame);};
  },[children]);
  return <div ref={element} className={'data-viewport '+className} role="region" aria-label={label} tabIndex={0}>{children}</div>;
}
