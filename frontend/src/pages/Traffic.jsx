import { traffic } from '../api/client'
import ModulePage from './ModulePage'

export default function Traffic() {
  return (
    <ModulePage
      title="Traffic Management"
      subtitle="Congestion prediction, signal optimization, and hotspot analysis"
      color="#f59e0b"
      fetchAnalytics={() => traffic.analytics()}
      mapOverlay="traffic"
      barKey="congestion"
      barNameKey="name"
    />
  )
}
