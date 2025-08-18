-- This script seeds the 'documents' table with ALL reference files.
-- Run it after running 'create_document_features.sql'.

BEGIN;

INSERT INTO documents (title, description, image, href) VALUES
--------------------------------------------------------------------------------
-- ░░ EXISTING ENTRIES (unchanged) ░░
--------------------------------------------------------------------------------
('Packct Spraying',
 'Technical notes on packet-spraying attack simulations',
 'https://images.unsplash.com/photo-1587574293341-ec07293cb447?auto=format&fit=crop&w=800&q=80',
 '/Packct-Spraying.pdf'),

('Bandwidth Works in Practice, not in Theory',
 'A real-world look at Ethernet performance versus the textbooks.',
 'https://images.unsplash.com/photo-1550745165-9bc0b252726a?auto=format&fit=crop&w=800&q=80',
 '/Bandwidth-Works-in-Practice-not-in-Theory.pdf'),

('LaTeX File Color Mapping',
 'Mapping macOS tag colors to .tex, .sty and project files.',
 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80',
 '/Latex-Files-and-Colors.numbers.pdf'),

('Ethernet: Distributed Packet Switching',
 'The original 1976 Metcalfe & Boggs Ethernet spec, straight from PARC.',
 'https://images.unsplash.com/photo-1534972195531-d756b9bfa9f2?auto=format&fit=crop&w=800&q=80',
 '/main.pdf'),

('Bandwidth Works in Practice (June 2025)',
 'June 2025 follow-up on practical throughput studies.',
 'https://images.unsplash.com/photo-1581094794329-c8112a89af10?auto=format&fit=crop&w=800&q=80',
 '/main2.pdf'),

('Ethernet Spec (Mirror)',
 'Alternate mirror of the classic Metcalfe & Boggs paper.',
 'https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80',
 '/main3.pdf'),

('Ethernet Spec (Full PDF)',
 'Yet another copy, just in case — complete and unabridged.',
 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
 '/Metcalfe+Boggs.pdf'),

('NDA – Dean Gladish',
 'Legal agreement governing our collaboration details.',
 'https://images.unsplash.com/photo-1556742031-c6961e8560b0?auto=format&fit=crop&w=800&q=80',
 '/NDA-Dean-Gladish-2025-06-04_23-06.pdf'),

('OAE Logo',
 'High-resolution vector of the Official Academic Emblem.',
 'https://images.unsplash.com/photo-1529676468690-a0ff4e722963?auto=format&fit=crop&w=800&q=80',
 '/OAE_Logo_copy.pdf'),

('Fig. 1 – Two-segment Ethernet',
 'Illustration showing dual-segment collision domains.',
 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80',
 '/Omni-Figure-1.pdf'),

('Reinventing Reliability at L2',
 'Modern take on making Ethernet reliable without extra bandwidth cost.',
 'https://images.unsplash.com/photo-1581091012184-38d3b93dc357?auto=format&fit=crop&w=800&q=80',
 '/Reinventing-Reliability-at-L2.pdf'),

('Ethernet Template Copy',
 'Yet another template copy — same as “main.pdf.”',
 'https://images.unsplash.com/photo-1573497169428-b8d87734a5a2?auto=format&fit=crop&w=800&q=80',
 '/template_copy.pdf'),

('Testing the Ethernet Figures',
 'Draft file with experimental diagrams for collision back-off.',
 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
 '/TEST-Ethernet-Figures.pdf'),

('Computer Systems – Bell, Fuller, Siewiorek',
 'Chapters on systems design, with an Ethernet overview.',
 'https://images.unsplash.com/photo-1519389950473-47ba0277781c?auto=format&fit=crop&w=800&q=80',
 '/test.pdf'),

('Welcome Dean – Introduction to Dædælus',
 'The “hello world” of Dædælus — our mission statement.',
 'https://images.unsplash.com/photo-1526401281623-3ad9882883b4?auto=format&fit=crop&w=800&q=80',
 '/Welcome-Dean.pdf'),

('FAQ – Graph Virtual Machine (GVM)',
 'Frequently asked questions on the design and usage of the GVM.',
 'https://images.unsplash.com/photo-1526401300632-2d7d2b50339b?auto=format&fit=crop&w=800&q=80',
 '/FAQ-GVM.pdf'),

('Reversibility & Time-Reversible Computing',
 'C. H. Bennett’s foundational paper on logical reversibility.',
 'https://images.unsplash.com/photo-1504386106331-3e4e71712b38?auto=format&fit=crop&w=800&q=80',
 '/Bennett_Reversibility.pdf'),

--------------------------------------------------------------------------------
-- ░░ NEW ENTRIES ░░
--------------------------------------------------------------------------------
('Open Atomic Ethernet Specification',
 'The main specification document for the Open Atomic Ethernet (OAE) workstream, detailing its principles, architecture, and protocols.',
 'https://images.unsplash.com/photo-1542224566-2e40f87baf79?auto=format&fit=crop&w=800&q=80',
 '/OAE-SPEC-MAIN.pdf'),

('Dean Gladish – Keynote Slides',
 'Core deck for Dean’s 2025 keynote.',
 'https://images.unsplash.com/photo-1555431189-0fabf43041d6?auto=format&fit=crop&w=800&q=80',
 '/DeansPresentation.pdf'),

('OCP-OAE 2025 – Evolving Interconnects',
 'OpenCompute/OAE joint white-paper on the 2025 roadmap.',
 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80',
 '/OCP-OAE-02025-EVOLVING.pdf'),

('Cellular Automata – From Classical Computation to QEC',
 'Survey linking CA research to modern quantum-error-correction.',
 'https://images.unsplash.com/photo-1529070538774-1843cb3265df?auto=format&fit=crop&w=800&q=80',
 '/CellularAutomata-FromClassicalComputationtoQuantumErrorCorrection.pdf'),

('Æthernet Talk (final)',
 'Conference talk: deterministic latency via interaction multiplexing.',
 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?auto=format&fit=crop&w=800&q=80',
 '/aethernet_talk_final.pdf'),

('The Distributed Firing-Squad Problem – Review',
 'Temporal inconsistencies between computation and physics (survey).',
 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?auto=format&fit=crop&w=800&q=80',
 '/TheDistributedFiringSquadProblem-AReviewofTemporalInconsistenciesBetweenComputationandPhysics.pdf'),

('PUF Talk',
 'Physically-Unclonable Functions & deterministic networking.',
 'https://images.unsplash.com/photo-1535223289827-42f1e9919769?auto=format&fit=crop&w=800&q=80',
 '/PUF_Talk.pdf'),

('Demolition 2',
 'Slide deck – tearing bandwidth myths apart (rev 2).',
 'https://images.unsplash.com/photo-1502877338535-766e1452684a?auto=format&fit=crop&w=800&q=80',
 '/Demolition2.pdf'),

('TR25-017 – Technical Report',
 'Internal TR on reversible simulations.',
 'https://images.unsplash.com/photo-1471864190281-2819886895b5?auto=format&fit=crop&w=800&q=80',
 '/TR25-017.pdf'),

('LIPIcs CCC 2022 §8',
 'Square-root space vs time trade-offs (conference version).',
 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?auto=format&fit=crop&w=800&q=80',
 '/LIPIcs.CCC.2022.8.pdf'),

('Square-Root Space',
 'Extended notes on √n-space lower bounds.',
 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80',
 '/Square-Root-Space.pdf'),

('Graph Report',
 'Topological invariants of interaction graphs.',
 'https://images.unsplash.com/photo-1534081333815-ae5019106622?auto=format&fit=crop&w=800&q=80',
 '/Graph-Report.pdf'),

('Inline Graphic 1',
 'Supporting figure for the spec.',
 'https://images.unsplash.com/photo-1533787761082-65d9f5f7f6ab?auto=format&fit=crop&w=800&q=80',
 '/PastedGraphic-1.png'),

('Inline Graphic 3',
 'Supplementary illustration.',
 'https://images.unsplash.com/photo-1533827432537-70133748f5c8?auto=format&fit=crop&w=800&q=80',
 '/PastedGraphic-3.png'),

('Aethernet Poster (JPEG)',
 'High-res conference poster.',
 'https://images.unsplash.com/photo-1506784983877-45594efa4cbe?auto=format&fit=crop&w=800&q=80',
 '/GuQqVMxbwAAMg4t.jpeg'),

('Principles of Operation (01)',
 'Foundational operations guide.',
 'https://images.unsplash.com/photo-1554384645-13eab165c24b?auto=format&fit=crop&w=800&q=80',
 '/01_principles-of_operation.pdf'),

('Distributed Firing-Squad (BN copy)',
 'Correctness proofs under bounded nondeterminism.',
 'https://images.unsplash.com/photo-1542224566-2e40f87baf79?auto=format&fit=crop&w=800&q=80',
 '/DistributedFiringSquadcopy-BN.pdf'),

('Screenshot – 07-02-2025 19-13-40',
 'UI mock-up of the new library view.',
 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80',
 '/Screenshot2025-07-02at7.13.40PM.png'),

--------------------------------------------------------------------------------
-- ░░ NEW ENTRIES (2025-07-09) ░░
--------------------------------------------------------------------------------
('Quantum Cellular Automata (QCA) Primer',
 'Introductory survey: QCA as a bridge between CA and quantum information.',
 'https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=800&q=80',
 '/QCA.pdf'),

('RDMA Meta-Protocol',
 'Design notes for an RDMA-accelerated meta-protocol in Ethernet 2025.',
 'https://images.unsplash.com/photo-1504386106331-3e4e71712b38?auto=format&fit=crop&w=800&q=80',
 '/RDMA-Meta.pdf'),

('TAP #120 — Set Reconciliation (Pat & Daniel)',
 'Time Appliances Project episode 120: provably-safe set reconciliation.',
 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=800&q=80',
 '/TAP120_Set-Reconcilliation-Pat-Daniel.pdf'),

('HammingMesh: A Network Topology for Large-Scale Deep Learning',
 'A novel network topology that provides high bandwidth at low cost with high job-scheduling flexibility, designed for large-scale deep learning systems.',
 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
 '/3623490_HammingMesh:_A_Network_Topology_for_Large-Scale_Deep_Learning.pdf'),

--------------------------------------------------------------------------------
-- ░░ NEW ENTRIES (2025-07-13) ░░
--------------------------------------------------------------------------------
('Cost and Bandwidth Comparison',
 'Detailed comparison of network topologies from the HammingMesh paper.',
 'https://images.unsplash.com/photo-1534447677768-be436bb09401?auto=format&fit=crop&w=800&q=80',
 '/PastedGraphic-1 (1).png'),

('Welcome, David – Dædælus Intro',
 'Introductory document for new team members, outlining the core problems Daedaelus addresses.',
 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80',
 '/Welcome-David.pdf'),

('Chiplet Mesh Networking (Apr 2024)',
 'Presentation on applying graph theory and novel protocols to chiplet mesh networks.',
 'https://images.unsplash.com/photo-1593640408182-31c70c8268f5?auto=format&fit=crop&w=800&q=80',
 '/Chiplet-Mesh-Networking-02024-Apr-18.pdf'),

('PROMELA Modeling for FSP',
 'Technical document on using PROMELA for modeling the Firing Squad Problem.',
 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=800&q=80',
 '/promela_modeling.pdf'),

('Dual SAW Petri-Spekkens Protocol',
 'Details the Dual Stop-and-Wait protocol using Petri Nets and the Spekkens Toy Model for epistricted consistency.',
 'https://images.unsplash.com/photo-1534723452862-4c874018d66d?auto=format&fit=crop&w=800&q=80',
 '/Dual-SAW-Spekkens.pdf'),

('The Evolution of Ethernet (2022)',
 'A 2022 perspective on Ethernets evolution, challenging classic assumptions and proposing optimizations for latency over bandwidth.',
 'https://images.unsplash.com/photo-1580582932707-520aed93a94d?auto=format&fit=crop&w=800&q=80',
 '/Ethernet2022.pdf'),

('Information is a Surprise',
 'Explores the concept that information is surprisal and must be paired, applying it to network protocols.',
 'https://images.unsplash.com/photo-1516259762381-22954d7d3ad2?auto=format&fit=crop&w=800&q=80',
 '/Information-Surprise.pdf'),

('Liveness Tensor',
 'Describes a transitively coherent data structure for liveness awareness in directly connected datacenter networks.',
 'https://images.unsplash.com/photo-1542744173-8e7e53415bb0?auto=format&fit=crop&w=800&q=80',
 '/Liveness_Tensor.pdf'),

('Project Requirements (Charlie-2)',
 'Core requirements for the Daedaelus project, including hardware targets and protocol state machine principles.',
 'https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80',
 '/Requirements-Charlie-2.pdf'),

('Slice Engine Specification',
 'Defines the protocol for processing 8-byte slices, confinement, and port-addressing solutions.',
 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=800&q=80',
 '/Slice-Engine.pdf'),

('State Machine Specification',
 'Defines the reversible state machine models, including 1-state, 2-state, and 4-state transfer protocols.',
 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80',
 '/State-Machine-Specification.pdf'),

('Superposition Engine',
 'Details the MORTS (Morphism pORTS) Open Petri Net Model for managing connected information and event ordering.',
 'https://images.unsplash.com/photo-1507146426996-32f275980346?auto=format&fit=crop&w=800&q=80',
 '/Superposition-Engine.pdf'),

 --------------------------------------------------------------------------------
-- ░░ NEW ENTRIES ░░
--------------------------------------------------------------------------------
('Slowdown Theorem on Links',
 'Critiques ''Forward-In-Time-Only'' thinking and proposes a reversible link protocol model that accounts for indefinite causality.',
 'https://images.unsplash.com/photo-1634733510042-41d35e5333e3?auto=format&fit=crop&w=800&q=80',
 '/Slowdown-Theorem-on-Links-FILE_3981.pdf'),

('FAQ – Bandwidth',
 'Compares the bandwidth and resilience of the Daedaelus Transaction Fabrix with conventional Clos networks.',
 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80',
 '/DAE-FAQ-Bandwidth_20230709a.pdf'),

('FAQ – Latency',
 'Explores the predictable, low-latency characteristics of the Transaction Fabrix versus the tail latency of switched networks.',
 'https://images.unsplash.com/photo-1587573750242-a162d42a92e3?auto=format&fit=crop&w=800&q=80',
 '/FAQ-Latency-2-copy.pdf'),

('Daedaelus Project Instructions',
 'Internal project notes, tasks, and discussions related to the Daedaelus platform and its development.',
 'https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=800&q=80',
 '/Instructions for Daedaelus.pdf'),

('Bandwidth Works in Practice, not in Theory (Sahas Resend)',
 'A version of the core Daedaelus thesis on reliable networking, challenging the industry''s focus on bandwidth over transactional integrity.',
 'https://images.unsplash.com/photo-1581094794329-c8112a89af10?auto=format&fit=crop&w=800&q=80',
 '/main-resend-Sahas.pdf'),

('Finite Automata and Decision Problems',
 'A deep dive into the theory of finite automata, their decision problems, and their foundational role in computer science, from the 1959 Rabin-Scott paper to modern applications.',
 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
 '/Finite-Automata.pdf'),

('Mulligan Stew FAQ',
 'A compilation of questions and detailed answers from the Daedaelus team, clarifying core concepts like atomicity, problem space, and architectural principles.',
 'https://images.unsplash.com/photo-1526401281623-3ad9882883b4?auto=format&fit=crop&w=800&q=80',
 '/Mulligan-Stew-FAQ.pdf'),

('Time-Optimal Firing Squad/Mob Synchronisation',
 'Simon Wacker''s paper on a time-optimal quasi-solution of the firing mob synchronisation problem on connected graphs, using signal machines and cellular automata.',
 'https://images.unsplash.com/photo-1593640408182-31c70c8268f5?auto=format&fit=crop&w=800&q=80',
 '/simon_wacker_graphFSP.pdf'),

('A Scalable, Commodity Data Center Network Architecture',
 'The influential 2008 SIGCOMM paper by Al-Fares, Loukissas, and Vahdat proposing a scalable data center architecture using fat-tree topologies with commodity switches.',
 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80',
 '/1402958.1402967.pdf'),

('Pat Helland''s Questions (Mulligan Stew FAQ)',
 'A focused FAQ addressing specific, challenging questions from Pat Helland regarding the core problem, participants, and definition of atomicity in the Daedaelus system.',
 'https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=800&q=80',
 '/PatHellandQuestions.pdf'),

 -- ░░ NEW ENTRIES (2025-08-17) ░░
('Arista',
 'Vendor architecture overview and reference PDF.',
 'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80',
 '/Arista.pdf'),

('Clos Fabric (OmniGraffle export)',
 'Clos fabric diagrams exported from OmniGraffle.',
 'https://images.unsplash.com/photo-1534081333815-ae5019106622?auto=format&fit=crop&w=800&q=80',
 '/Clos-Fabric.graffle.pdf'),

('Conventional Networking',
 'Overview of conventional (pre-transactional) networking designs.',
 'https://images.unsplash.com/photo-1581093448795-5f9f0c2a1f2c?auto=format&fit=crop&w=800&q=80',
 '/ConventionalNetworking.pdf'),

('Ethernet Animation (legacy)',
 'Legacy animated slides illustrating historical behaviors.',
 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80',
 '/Old-Animated.pdf'),

('Transaction Processing Spec',
 'Daedaelus transaction-processing specification (draft).',
 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?auto=format&fit=crop&w=800&q=80',
 '/Tranzaction-Processing-Spec.pdf'),

ON CONFLICT (href) DO NOTHING;   -- safe to re-run

COMMIT;
