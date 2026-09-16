import React from 'react';
import type { EnvironmentalProfile } from '@/types';
import { Droplet, ThermometerSun, Leaf, Sprout, Factory, MapPin } from 'lucide-react';

export default function EnvironmentalPanel({ profile }: { profile: EnvironmentalProfile | null }) {
  if (!profile) {
    return (
      <div className="p-6 text-center text-gray-500 flex flex-col items-center justify-center h-full">
        <MapPin className="w-12 h-12 mb-3 opacity-20" />
        <p className="text-sm">No active environmental profile.</p>
        <p className="text-xs mt-1">Start a conversation or load a scenario.</p>
      </div>
    );
  }

  const Metric = ({ label, value }: { label: string, value: any }) => (
    <div className="flex justify-between items-center py-1.5 border-b border-earth-border/50 last:border-0">
      <span className="text-xs text-gray-400">{label}</span>
      <span className="text-xs font-medium text-gray-200">
        {value !== undefined && value !== null && value !== '' ? value : <span className="text-gray-600">Missing</span>}
      </span>
    </div>
  );

  return (
    <div className="p-4 space-y-4 overflow-y-auto h-full pb-20">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-white mb-1">Context Profile</h2>
        <div className="text-sm text-earth-accent flex items-center gap-1.5">
          <MapPin className="w-3.5 h-3.5" />
          {profile.region || 'Unknown Region'}
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Droplet className="w-4 h-4 text-blue-400" /> Soil Health
        </h3>
        <div className="space-y-1">
          <Metric label="pH Level" value={profile.soil?.ph} />
          <Metric label="Organic Carbon (%)" value={profile.soil?.organic_carbon_percent} />
          <Metric label="Moisture (%)" value={profile.soil?.moisture_percent} />
          <Metric label="Structure" value={profile.soil?.structure} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <ThermometerSun className="w-4 h-4 text-orange-400" /> Climate
        </h3>
        <div className="space-y-1">
          <Metric label="Temp (°C)" value={profile.climate?.temperature_c} />
          <Metric label="Rainfall (mm)" value={profile.climate?.rainfall_mm} />
          <Metric label="Pattern" value={profile.climate?.rainfall_pattern} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Sprout className="w-4 h-4 text-green-400" /> Land Use
        </h3>
        <div className="space-y-1">
          <Metric label="Primary Type" value={profile.land_use?.primary_type} />
          <Metric label="Cropping System" value={profile.land_use?.cropping_system} />
          <Metric label="Main Crop" value={profile.land_use?.crop} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Leaf className="w-4 h-4 text-emerald-400" /> Biodiversity
        </h3>
        <div className="space-y-1">
          <Metric label="Species Richness" value={profile.biodiversity?.species_richness} />
          <Metric label="Habitat Diversity" value={profile.biodiversity?.habitat_diversity} />
          <Metric label="Pollinators" value={profile.biodiversity?.pollinator_presence} />
        </div>
      </div>

      <div className="bg-earth-card border border-earth-border rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-100 flex items-center gap-2 mb-3">
          <Factory className="w-4 h-4 text-gray-400" /> Human Impact
        </h3>
        <div className="space-y-1">
          <Metric label="Pesticide Pressure" value={profile.human_impact?.pesticide_pressure} />
          <Metric label="Pollution Level" value={profile.human_impact?.pollution_level} />
          <Metric label="Deforestation" value={profile.human_impact?.deforestation_pressure} />
        </div>
      </div>
    </div>
  );
}
