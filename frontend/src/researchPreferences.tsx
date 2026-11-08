import {createContext,useContext,useState,type Dispatch,type SetStateAction,type ReactNode} from 'react';
type Store={state:Record<string,unknown>;setState:Dispatch<SetStateAction<Record<string,unknown>>>};
const Preferences=createContext<Store|null>(null);
export function ResearchPreferencesProvider({children}:{children:ReactNode}){const [state,setState]=useState<Record<string,unknown>>({});return <Preferences.Provider value={{state,setState}}>{children}</Preferences.Provider>;}
// UI choices only, held for the unlocked workspace. No credentials or market data.
export function useResearchPreference<T,>(key:string,initial:T):[T,Dispatch<SetStateAction<T>>]{
 const context=useContext(Preferences),[local,setLocal]=useState(initial);
 if(!context)return [local,setLocal];
 return [(context.state[key] as T|undefined)??initial,update=>context.setState(old=>({...old,[key]:typeof update==='function'?(update as (old:T)=>T)((old[key] as T|undefined)??initial):update}))];
}
