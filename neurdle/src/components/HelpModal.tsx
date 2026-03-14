interface Props { onClose: () => void; }

export default function HelpModal({ onClose }: Props) {
  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-[#1a1a2e] rounded-2xl p-6 max-w-md w-full border border-white/20 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-white">How to Play</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl leading-none">&times;</button>
        </div>

        <div className="space-y-3 text-gray-300 text-sm">
          <p>Identify the 3D brain region shown. You have <strong className="text-white">6 guesses</strong>.</p>
          <p>After each wrong guess you get feedback:</p>
          <ul className="list-disc list-inside space-y-1.5 ml-2">
            <li><strong className="text-white">Distance</strong>: How far your guess is from the target (mm)</li>
            <li><strong className="text-white">Proximity %</strong>: 100% = correct, 0% = opposite end of brain</li>
            <li><strong className="text-white">Direction</strong>: Which way to go (anterior, superior, etc.)</li>
          </ul>

          <div className="border-t border-white/10 pt-3">
            <p className="font-medium text-white mb-1.5">Modes:</p>
            <p><span className="text-white">📅 Daily</span>: One puzzle per difficulty per day</p>
            <p><span className="text-white">📚 Training</span>: Unlimited play, track your score</p>
          </div>

          <div className="border-t border-white/10 pt-3">
            <p className="font-medium text-white mb-1.5">Difficulty tiers:</p>
            <p><span className="text-white">Easy</span>: brain lobes, cerebellum, brainstem</p>
            <p><span className="text-white">Normal</span>: 34 Desikan-Killiany cortical regions + major subcortical + brainstem subregions + major white matter tracts</p>
            <p><span className="text-white">Hard</span>: 74 Destrieux atlas regions (fine gyri and sulci)</p>
          </div>
        </div>

        <div className="border-t border-white/10 mt-4 pt-4 space-y-2 text-xs text-gray-400">
          <p className="font-medium text-gray-300">Credits</p>
          <p>
            Brain atlas data from{' '}
            <a href="https://surfer.nmr.mgh.harvard.edu" target="_blank" rel="noopener noreferrer"
               className="text-[#e94560] hover:underline">FreeSurfer</a>{' '}
            fsaverage: Desikan-Killiany and Destrieux parcellations.
          </p>
          <p>HEAVILY Inspired by <a href="https://www.nytimes.com/games/wordle" target="_blank" rel="noopener noreferrer" className="text-[#e94560] hover:underline">Wordle</a> and <a href="https://worldle.teuteuf.fr" target="_blank" rel="noopener noreferrer" className="text-[#e94560] hover:underline">Worldle</a>.</p>
          <p>
            Project source code on{' '}
            <a href="https://github.com/AlexanderAtalay/neurdle" target="_blank" rel="noopener noreferrer"
               className="text-[#e94560] hover:underline">
              GitHub ↗
            </a>
          </p>
          <p>
            Created by{' '}
            <a href="https://alexanderatalay.com" target="_blank" rel="noopener noreferrer"
               className="text-[#e94560] hover:underline">
              Alexander Atalay
            </a>
          </p>
          <p>Conceived of by Alexander Atalay, Grant Mannino, Gracie Grimsrud, and Lucy Anderson</p>
        </div>

        <button
          onClick={onClose}
          className="mt-4 w-full py-2 bg-[#e94560] text-white rounded-lg font-medium hover:bg-[#c73450] transition-colors"
        >
          Got it
        </button>
      </div>
    </div>
  );
}
