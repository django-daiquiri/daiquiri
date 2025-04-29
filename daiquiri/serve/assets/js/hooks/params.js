import { useContext, createContext } from 'react'


const ServeParamsContext = createContext();
export const useServeParams = () => {
  const context = useContext(ServeParamsContext);
  return context !== undefined ? context : {}
}
export const ServeParamsProvider = ServeParamsContext.Provider;
