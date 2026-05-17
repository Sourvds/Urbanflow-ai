import { water } from '../api/client'
import ModulePage from './ModulePage'

export default function Water() {
  return (
    <ModulePage
      title="Water Distribution"
      subtitle="Demand forecasting, leak detection, and pressure optimization"
      color="#3b82f6"
      fetchAnalytics={() => water.analytics()}
      mapOverlay="water"
      barKey="consumption"
      barNameKey="name"
    />
  )
}
