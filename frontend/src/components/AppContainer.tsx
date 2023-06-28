import React from 'react'

interface AppContainerProps {
    children: React.ReactNode,
    styles?: React.CSSProperties
}

export default function AppContainer(props: AppContainerProps) {
  return (
    <div  style={{ maxWidth: 1520, marginInline: "auto", paddingInline: 12, ...props.styles }}>{props.children}</div>
  )
}
