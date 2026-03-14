'use client';
import { Suspense, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, useGLTF, Center, Environment } from '@react-three/drei';
import type { Region } from '@/types';

// FreeSurfer RAS (Z=superior) → Three.js (Y=up)
const RAS_TO_THREEJS: [number, number, number] = [-Math.PI / 2, 0, 0];

function ColoredRegion({ meshFile, color, opacity = 1 }: {
  meshFile: string; color: string; opacity?: number;
}) {
  const { scene } = useGLTF(`/meshes/${meshFile}`);
  const cloned = useMemo(() => {
    const c = scene.clone(true);
    c.traverse((child: any) => {
      if (child.isMesh) {
        child.material = child.material.clone();
        child.material.color.set(color);
        child.material.roughness = 0.6;
        child.material.metalness = 0.1;
        if (opacity < 1) {
          child.material.transparent = true;
          child.material.opacity = opacity;
          child.material.depthWrite = false;
        }
      }
    });
    return c;
  }, [scene, color, opacity]);
  return <primitive object={cloned} />;
}

function RegionGroup({ region, color, opacity }: {
  region: Region; color: string; opacity?: number;
}) {
  const files = region.mesh_files ?? [region.mesh_file];
  return (
    <>
      {files.map(f => (
        <ColoredRegion key={f} meshFile={f} color={color} opacity={opacity} />
      ))}
    </>
  );
}

function GlassHemi({ path }: { path: string }) {
  const { scene } = useGLTF(path);
  const cloned = useMemo(() => {
    const c = scene.clone(true);
    c.traverse((child: any) => {
      if (child.isMesh) {
        child.material = child.material.clone();
        child.material.transparent = true;
        child.material.opacity = 0.12;
        child.material.color.set('#8888cc');
        child.material.depthWrite = false;
      }
    });
    return c;
  }, [scene]);
  return <primitive object={cloned} />;
}

function GlassBrain() {
  return (
    <>
      <GlassHemi path="/meshes/whole_brain_ghost_L.glb" />
      <GlassHemi path="/meshes/whole_brain_ghost_R.glb" />
    </>
  );
}

interface Props {
  targetRegion: Region | null;
  showGlassBrain: boolean;
  wrongGuessRegions?: Region[];  // shown at low opacity (training mode)
}

export default function BrainViewer({ targetRegion, showGlassBrain, wrongGuessRegions = [] }: Props) {
  return (
    <div className="w-full h-full rounded-xl overflow-hidden bg-[#0d0d1a]">
      <Canvas
        camera={{ position: [-107, 20, -160], fov: 45 }}
        gl={{ antialias: true }}
      >
        <ambientLight intensity={0.6} />
        <directionalLight position={[50, 50, 50]} intensity={1.2} />
        <directionalLight position={[-50, -30, -50]} intensity={0.4} />
        <Environment preset="studio" />

        <OrbitControls
          enablePan enableZoom enableRotate
          autoRotate autoRotateSpeed={0.3}
          minDistance={20} maxDistance={300}
        />

        <group rotation={RAS_TO_THREEJS}>
          <Suspense fallback={null}>
            <Center>
              {targetRegion && (
                <RegionGroup key={targetRegion.id} region={targetRegion} color="#e94560" />
              )}
              {showGlassBrain && <GlassBrain />}
              {wrongGuessRegions.map(r => (
                <RegionGroup key={r.id} region={r} color="#ff8c42" opacity={0.35} />
              ))}
            </Center>
          </Suspense>
        </group>
      </Canvas>
    </div>
  );
}
