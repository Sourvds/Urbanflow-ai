import { electricity } from '../api/client'
import ModulePage from './ModulePage'

export default function Electricity() {
  return (
    <ModulePage
      title="Electricity Optimization"
      subtitle="Demand forecasting, peak analysis, and anomaly detection"
      color="#00d4ff"
      fetchAnalytics={() => electricity.analytics()}
      mapOverlay="electricity"
      barKey="avg_kwh"
      barNameKey="name"
    />
  )
}
