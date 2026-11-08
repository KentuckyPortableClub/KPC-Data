# 2-fer accuracy check: CA-NB

Run 2026-11-08T05:35:34Z → 2026-11-08T05:59:06Z (UTC) · tool 0.1.0 (2026-10-31) · complete
Live rows in the file: 409 · checked: 409 · skipped (dropped / merged): 338

| verdict | rows |
|---|---|
| CONFIRMED | 225 |
| SHRUNK | 22 |
| GREW | 24 |
| MOVED | 50 |
| GONE | 88 |

| flag | rows |
|---|---|
| small overlap (under 50 yd across) | 72 |

## For a person to look at

- **SHRUNK** `CA-0024+CA-4535+CA-6535@area@45.633,-64.964`: only 61% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-0025+CA-4535+CA-6535@area@45.633,-64.964`: only 61% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-0073+CA-1238+CA-6539@area@45.960,-66.367`: live overlap is 95% smaller (0.1 ac vs 1.7 ac stored)
- **SHRUNK** `CA-0772+CA-4524+CA-6518@area@47.359,-65.538`: live overlap is 91% smaller (0.1 ac vs 0.7 ac stored)
- **SHRUNK** `CA-0772+CA-4525+CA-6518@area@47.359,-65.538`: live overlap is 91% smaller (0.1 ac vs 0.7 ac stored)
- **SHRUNK** `CA-0788+CA-6549@area@47.454,-66.973`: live overlap is 94% smaller (0.6 ac vs 10.9 ac stored)
- **SHRUNK** `CA-1225+CA-4425+CA-6503@area@45.828,-64.806`: live overlap is 94% smaller (0.5 ac vs 7.5 ac stored)
- **SHRUNK** `CA-1257+CA-4456+CA-6545@area@47.671,-66.650`: live overlap is 100% smaller (0.0 ac vs 7.1 ac stored)
- **SHRUNK** `CA-1257+CA-4473+CA-6545@area@47.666,-66.715`: live overlap is 48% smaller (0.1 ac vs 0.2 ac stored)
- **SHRUNK** `CA-4362+CA-6547@area@47.763,-68.293`: live overlap is 84% smaller (0.3 ac vs 1.7 ac stored)
- **SHRUNK** `CA-4372+CA-6545@area@47.780,-67.379`: live overlap is 86% smaller (1.2 ac vs 9.3 ac stored)
- **SHRUNK** `CA-4379+CA-4498+CA-6518@area@47.583,-65.226`: live overlap is 84% smaller (0.8 ac vs 5.0 ac stored)
- **SHRUNK** `CA-4385+CA-4391+CA-6537@area@45.898,-67.627`: live overlap is 100% smaller (0.0 ac vs 2.9 ac stored)
- **SHRUNK** `CA-4422+CA-4538+CA-6509@area@46.297,-65.546`: live overlap is 99% smaller (0.0 ac vs 1.0 ac stored)
- **SHRUNK** `CA-4430+CA-6234+CA-6535@area@45.502,-65.309`: live overlap is 100% smaller (0.0 ac vs 4.8 ac stored)
- **SHRUNK** `CA-4440+CA-4465+CA-6538@area@46.327,-67.100`: live overlap is 100% smaller (0.0 ac vs 16.8 ac stored)
- **SHRUNK** `CA-4440+CA-4510+CA-6538@area@46.325,-67.128`: live overlap is 86% smaller (0.4 ac vs 2.6 ac stored)
- **SHRUNK** `CA-4478+CA-4479+CA-6509@area@45.995,-65.819`: live overlap is 95% smaller (0.0 ac vs 0.7 ac stored)
- **SHRUNK** `CA-4535+CA-6535@area@45.628,-64.967`: live overlap is 98% smaller (0.6 ac vs 25.7 ac stored)
- **SHRUNK** `CA-5187+CA-6518@area@47.230,-65.103`: live overlap is 39% smaller (1.2 ac vs 1.9 ac stored)
- **SHRUNK** `CA-5235+CA-6538@area@46.043,-66.852`: only 61% of the stored overlap is still inside the live overlap (10 m tolerance)
- **SHRUNK** `CA-6546+CA-6549@area@47.513,-67.392`: live overlap is 100% smaller (0.2 ac vs 50.4 ac stored)
- **GREW** `CA-0072+CA-6518@area@47.170,-65.045`: live overlap is 100% bigger (822.2 ac vs 410.4 ac stored); 90% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-0073+CA-6539@area@45.912,-66.367`: live overlap is 43% bigger (2110.3 ac vs 1479.7 ac stored); 80% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-0090+CA-6503@area@45.698,-64.781`: live overlap is 89% bigger (1724.2 ac vs 910.6 ac stored); 96% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-1224+CA-6535@area@45.296,-66.124`: live overlap is 80% bigger (58.4 ac vs 32.5 ac stored); 92% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-1226+CA-6503@area@45.599,-64.782`: live overlap is 55% bigger (69.7 ac vs 44.9 ac stored); 93% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-1245+CA-6508@area@45.400,-66.023`: live overlap is 116% bigger (234.4 ac vs 108.5 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-1249+CA-6539@area@45.908,-66.162`: live overlap is 43% bigger (204.0 ac vs 142.8 ac stored); 87% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-1250+CA-6518@area@47.789,-65.255`: live overlap is 97% bigger (0.9 ac vs 0.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-1253+CA-6508@area@45.340,-66.102`: live overlap is 62% bigger (10.6 ac vs 6.6 ac stored); 80% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4357+CA-6538@area@46.365,-67.374`: live overlap is 61% bigger (185.4 ac vs 114.9 ac stored); 82% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4420+CA-6518@area@47.193,-65.823`: live overlap is 141% bigger (119.2 ac vs 49.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-4808+CA-6542@area@46.971,-65.576`: live overlap is 132% bigger (176.8 ac vs 76.4 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5150+CA-6537@area@46.124,-67.637`: live overlap is 54% bigger (157.8 ac vs 102.3 ac stored); 96% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5153+CA-6538@area@46.205,-66.608`: live overlap is 261% bigger (5.9 ac vs 1.6 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5167+CA-6540@area@46.360,-67.562`: live overlap is 90% bigger (31.3 ac vs 16.4 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5195+CA-6503@area@45.821,-65.052`: live overlap is 110% bigger (162.3 ac vs 77.4 ac stored); 96% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5208+CA-6527@area@45.881,-66.414`: live overlap is 385% bigger (230.6 ac vs 47.6 ac stored); 93% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5216+CA-6508@area@45.363,-66.059`: live overlap is 612% bigger (103.9 ac vs 14.6 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5218+CA-6508@area@45.499,-65.991`: live overlap is 82% bigger (13.9 ac vs 7.7 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5225+CA-6538@area@46.038,-66.710`: live overlap is 57% bigger (91.6 ac vs 58.2 ac stored); 95% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-5251+CA-6527@area@45.972,-66.801`: live overlap is 64% bigger (24.3 ac vs 14.8 ac stored); 98% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-6389+CA-6504@area@46.309,-64.588`: live overlap is 67% bigger (225.0 ac vs 134.5 ac stored); 100% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-6390+CA-6508@area@45.906,-65.788`: live overlap is 61% bigger (187.3 ac vs 116.4 ac stored); 97% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **GREW** `CA-6497+CA-6518@area@47.789,-65.255`: live overlap is 86% bigger (0.8 ac vs 0.4 ac stored); 99% of the stored overlap still inside (10 m tolerance): the stored row may carry an ownership / water mask this tool does not re-apply, or be one piece of a longer stretch
- **MOVED** `CA-0024+CA-4446+CA-6535@area@45.646,-65.142`: live overlap centre is 493 m from the stored centre; 11% of the stored overlap is still inside it
- **MOVED** `CA-0024+CA-4487+CA-6535@area@45.596,-65.121`: live overlap centre is 2993 m from the stored centre; 5% of the stored overlap is still inside it
- **MOVED** `CA-0024+CA-4535+CA-6503@area@45.634,-64.959`: live overlap centre is 344 m from the stored centre; 17% of the stored overlap is still inside it
- **MOVED** `CA-0024+CA-6503+CA-6535@area@45.706,-64.955`: live overlap centre is 1672 m from the stored centre; 1% of the stored overlap is still inside it
- **MOVED** `CA-0024+CA-6503@area@45.670,-65.106`: live overlap centre is 2072 m from the stored centre; 9% of the stored overlap is still inside it
- **MOVED** `CA-0025+CA-4446+CA-6535@area@45.646,-65.142`: live overlap centre is 493 m from the stored centre; 11% of the stored overlap is still inside it
- **MOVED** `CA-0025+CA-4487+CA-6535@area@45.596,-65.121`: live overlap centre is 2993 m from the stored centre; 5% of the stored overlap is still inside it
- **MOVED** `CA-0025+CA-4535+CA-6503@area@45.634,-64.959`: live overlap centre is 344 m from the stored centre; 17% of the stored overlap is still inside it
- **MOVED** `CA-0025+CA-6503+CA-6535@area@45.706,-64.955`: live overlap centre is 1672 m from the stored centre; 1% of the stored overlap is still inside it
- **MOVED** `CA-0025+CA-6503@area@45.670,-65.106`: live overlap centre is 2072 m from the stored centre; 9% of the stored overlap is still inside it
- **MOVED** `CA-0046+CA-4369+CA-6507@area@46.853,-65.035`: live overlap centre is 429 m from the stored centre; 7% of the stored overlap is still inside it
- **MOVED** `CA-1222+CA-4410+CA-6545@area@47.828,-66.730`: live overlap centre is 260 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-1229+CA-4387+CA-6546@area@47.877,-68.286`: live overlap centre is 254 m from the stored centre; 23% of the stored overlap is still inside it
- **MOVED** `CA-4368+CA-4503+CA-6535@area@45.473,-65.427`: live overlap centre is 539 m from the stored centre; 5% of the stored overlap is still inside it
- **MOVED** `CA-4369+CA-4412+CA-6507@area@46.920,-65.096`: live overlap centre is 395 m from the stored centre; 7% of the stored overlap is still inside it
- **MOVED** `CA-4388+CA-4430+CA-6535@area@45.510,-65.260`: live overlap centre is 295 m from the stored centre; 6% of the stored overlap is still inside it
- **MOVED** `CA-4389+CA-6545@area@47.758,-67.448`: live overlap centre is 301 m from the stored centre; 21% of the stored overlap is still inside it
- **MOVED** `CA-4411+CA-4471+CA-6537@area@45.832,-67.752`: live overlap centre is 248 m from the stored centre; 15% of the stored overlap is still inside it
- **MOVED** `CA-4454+CA-4471+CA-6537@area@45.850,-67.776`: live overlap centre is 308 m from the stored centre; 19% of the stored overlap is still inside it
- **MOVED** `CA-4454+CA-6103+CA-6537@area@45.850,-67.776`: live overlap centre is 308 m from the stored centre; 19% of the stored overlap is still inside it
- **MOVED** `CA-4455+CA-6547@area@47.716,-68.148`: live overlap centre is 1639 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-4499+CA-6504+CA-6507@area@46.513,-65.180`: live overlap centre is 794 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-4535+CA-6503+CA-6535@area@45.627,-64.969`: live overlap centre is 1134 m from the stored centre; 4% of the stored overlap is still inside it
- **MOVED** `CA-6503+CA-6508@area@46.023,-65.053`: live overlap centre is 6047 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6503+CA-6535@area@45.709,-64.955`: live overlap centre is 2000 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6504+CA-6505@area@46.243,-64.535`: live overlap centre is 23638 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6504+CA-6507@area@46.514,-65.116`: live overlap centre is 8084 m from the stored centre; 1% of the stored overlap is still inside it
- **MOVED** `CA-6507+CA-6551@area@46.997,-65.553`: live overlap centre is 13155 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6508+CA-6535@area@45.736,-65.512`: live overlap centre is 2283 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6508+CA-6539@area@45.952,-66.031`: live overlap centre is 200 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6509+CA-6539@area@46.238,-65.856`: live overlap centre is 34357 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6518+CA-6542@area@47.376,-66.072`: live overlap centre is 14238 m from the stored centre; 10% of the stored overlap is still inside it
- **MOVED** `CA-6518+CA-6544@area@47.510,-65.672`: live overlap centre is 5765 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6527+CA-6537@area@45.874,-66.926`: live overlap centre is 4160 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6537+CA-6540@area@46.158,-67.739`: live overlap centre is 878 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6538+CA-6539@area@46.362,-66.556`: live overlap centre is 40764 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6538+CA-6541@area@46.544,-67.171`: live overlap centre is 6222 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6538+CA-6550@area@46.423,-66.682`: live overlap centre is 19069 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6539+CA-6550@area@46.560,-66.126`: live overlap centre is 25264 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6540+CA-6541@area@46.848,-67.312`: live overlap centre is 16918 m from the stored centre; 6% of the stored overlap is still inside it
- **MOVED** `CA-6540+CA-6549@area@47.017,-67.616`: live overlap centre is 1194 m from the stored centre; 4% of the stored overlap is still inside it
- **MOVED** `CA-6541+CA-6549@area@47.302,-67.065`: live overlap centre is 2423 m from the stored centre; 1% of the stored overlap is still inside it
- **MOVED** `CA-6541+CA-6550@area@46.865,-66.771`: live overlap centre is 40504 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6542+CA-6544@area@47.595,-66.272`: live overlap centre is 23356 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6542+CA-6545@area@47.539,-66.505`: live overlap centre is 11238 m from the stored centre; 10% of the stored overlap is still inside it
- **MOVED** `CA-6542+CA-6550@area@46.843,-66.037`: live overlap centre is 26736 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6544+CA-6545@area@48.001,-66.275`: live overlap centre is 50263 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6545+CA-6546@area@47.844,-67.374`: live overlap centre is 1065 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6547+CA-6549@area@47.472,-67.393`: live overlap centre is 514 m from the stored centre; 0% of the stored overlap is still inside it
- **MOVED** `CA-6550+CA-6551@area@46.824,-65.789`: live overlap centre is 38863 m from the stored centre; 1% of the stored overlap is still inside it
- **GONE** `CA-0024+CA-4535+CA-6503+CA-6535@area@45.639,-64.955`: no overlap between the live official outlines near this spot
- **GONE** `CA-0025+CA-4535+CA-6503+CA-6535@area@45.639,-64.955`: no overlap between the live official outlines near this spot
- **GONE** `CA-0771+CA-6547+CA-6548@area@47.446,-68.400`: no overlap between the live official outlines near this spot
- **GONE** `CA-0771+CA-6547@area@47.446,-68.400`: no overlap between the live official outlines near this spot
- **GONE** `CA-0780+CA-1233+CA-6550@area@46.767,-66.572`: no overlap between the live official outlines near this spot
- **GONE** `CA-0780+CA-6542+CA-6550@area@46.778,-66.299`: no overlap between the live official outlines near this spot
- **GONE** `CA-0788+CA-4466+CA-6542@area@47.367,-66.693`: no overlap between the live official outlines near this spot
- **GONE** `CA-0788+CA-6542+CA-6549@area@47.422,-66.972`: no overlap between the live official outlines near this spot
- **GONE** `CA-1235+CA-4409+CA-6548@area@47.232,-68.975`: no overlap between the live official outlines near this spot
- **GONE** `CA-1257+CA-4491+CA-6545@area@47.674,-66.658`: no overlap between the live official outlines near this spot
- **GONE** `CA-4349+CA-6541+CA-6542@area@47.100,-66.865`: no overlap between the live official outlines near this spot
- **GONE** `CA-4349+CA-6541@area@47.100,-66.865`: no overlap between the live official outlines near this spot
- **GONE** `CA-4361+CA-6546+CA-6547@area@47.568,-67.691`: no overlap between the live official outlines near this spot
- **GONE** `CA-4361+CA-6547@area@47.568,-67.691`: no overlap between the live official outlines near this spot
- **GONE** `CA-4362+CA-6546+CA-6547@area@47.763,-68.294`: no overlap between the live official outlines near this spot
- **GONE** `CA-4367+CA-6542+CA-6550@area@46.795,-66.197`: no overlap between the live official outlines near this spot
- **GONE** `CA-4372+CA-6545+CA-6546@area@47.789,-67.395`: no overlap between the live official outlines near this spot
- **GONE** `CA-4375+CA-6508+CA-6509@area@46.023,-65.623`: no overlap between the live official outlines near this spot
- **GONE** `CA-4382+CA-4542+CA-6538@area@46.158,-67.310`: no overlap between the live official outlines near this spot
- **GONE** `CA-4389+CA-6545+CA-6546@area@47.760,-67.446`: no overlap between the live official outlines near this spot
- **GONE** `CA-4411+CA-6103+CA-6537@area@45.832,-67.752`: no overlap between the live official outlines near this spot
- **GONE** `CA-4418+CA-4435+CA-6546@area@47.586,-67.595`: no overlap between the live official outlines near this spot
- **GONE** `CA-4418+CA-6546+CA-6547@area@47.546,-67.620`: no overlap between the live official outlines near this spot
- **GONE** `CA-4422+CA-6509+CA-6551@area@46.358,-65.537`: no overlap between the live official outlines near this spot
- **GONE** `CA-4422+CA-6551@area@46.358,-65.538`: no overlap between the live official outlines near this spot
- **GONE** `CA-4431+CA-4472+CA-6542@area@46.951,-66.415`: no overlap between the live official outlines near this spot
- **GONE** `CA-4440+CA-4465+CA-4510+CA-6538@area@46.325,-67.128`: no overlap between the live official outlines near this spot
- **GONE** `CA-4455+CA-6546+CA-6547@area@47.716,-68.147`: no overlap between the live official outlines near this spot
- **GONE** `CA-4456+CA-6544+CA-6545@area@47.679,-66.466`: no overlap between the live official outlines near this spot
- **GONE** `CA-4456+CA-6544@area@47.677,-66.449`: no overlap between the live official outlines near this spot
- **GONE** `CA-4465+CA-4510+CA-6538@area@46.325,-67.129`: no overlap between the live official outlines near this spot
- **GONE** `CA-4465+CA-4537+CA-6538@area@46.423,-67.168`: no overlap between the live official outlines near this spot
- **GONE** `CA-4468+CA-6541+CA-6549@area@47.241,-67.151`: no overlap between the live official outlines near this spot
- **GONE** `CA-4468+CA-6541@area@47.241,-67.149`: no overlap between the live official outlines near this spot
- **GONE** `CA-4531+CA-6509+CA-6551@area@46.453,-65.353`: no overlap between the live official outlines near this spot
- **GONE** `CA-4531+CA-6509@area@46.451,-65.357`: no overlap between the live official outlines near this spot
- **GONE** `CA-6503+CA-6504+CA-6505@area@46.092,-64.764`: no overlap between the live official outlines near this spot
- **GONE** `CA-6503+CA-6504+CA-6508@area@46.022,-65.034`: no overlap between the live official outlines near this spot
- **GONE** `CA-6503+CA-6504@area@46.092,-64.764`: no overlap between the live official outlines near this spot
- **GONE** `CA-6503+CA-6505@area@46.092,-64.763`: no overlap between the live official outlines near this spot
- **GONE** `CA-6503+CA-6508+CA-6535@area@45.787,-65.345`: no overlap between the live official outlines near this spot
- **GONE** `CA-6504+CA-6507+CA-6551@area@46.491,-65.264`: no overlap between the live official outlines near this spot
- **GONE** `CA-6504+CA-6508+CA-6509@area@46.056,-65.067`: no overlap between the live official outlines near this spot
- **GONE** `CA-6504+CA-6508@area@46.056,-65.068`: no overlap between the live official outlines near this spot
- **GONE** `CA-6504+CA-6509+CA-6551@area@46.487,-65.260`: no overlap between the live official outlines near this spot
- **GONE** `CA-6504+CA-6509@area@46.487,-65.260`: no overlap between the live official outlines near this spot
- **GONE** `CA-6504+CA-6551@area@46.491,-65.264`: no overlap between the live official outlines near this spot
- **GONE** `CA-6507+CA-6518+CA-6542+CA-6551@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6507+CA-6518+CA-6542@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6507+CA-6518+CA-6551@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6507+CA-6518@area@47.082,-65.353`: no overlap between the live official outlines near this spot
- **GONE** `CA-6507+CA-6542+CA-6551@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6507+CA-6542@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6508+CA-6509+CA-6539@area@45.954,-66.030`: no overlap between the live official outlines near this spot
- **GONE** `CA-6508+CA-6509@area@46.083,-65.402`: no overlap between the live official outlines near this spot
- **GONE** `CA-6508+CA-6527+CA-6539@area@45.780,-66.111`: no overlap between the live official outlines near this spot
- **GONE** `CA-6508+CA-6527@area@45.780,-66.111`: no overlap between the live official outlines near this spot
- **GONE** `CA-6509+CA-6539+CA-6551@area@46.238,-65.856`: no overlap between the live official outlines near this spot
- **GONE** `CA-6509+CA-6551@area@46.487,-65.260`: no overlap between the live official outlines near this spot
- **GONE** `CA-6518+CA-6542+CA-6551@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6518+CA-6543@area@47.791,-65.255`: no overlap between the live official outlines near this spot
- **GONE** `CA-6518+CA-6551@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6527+CA-6537+CA-6538@area@45.874,-66.927`: no overlap between the live official outlines near this spot
- **GONE** `CA-6527+CA-6538+CA-6539@area@45.955,-66.629`: no overlap between the live official outlines near this spot
- **GONE** `CA-6527+CA-6538@area@45.983,-66.768`: no overlap between the live official outlines near this spot
- **GONE** `CA-6527+CA-6539@area@45.954,-66.628`: no overlap between the live official outlines near this spot
- **GONE** `CA-6537+CA-6538+CA-6540@area@46.147,-67.566`: no overlap between the live official outlines near this spot
- **GONE** `CA-6537+CA-6538@area@46.147,-67.566`: no overlap between the live official outlines near this spot
- **GONE** `CA-6538+CA-6539+CA-6550@area@46.362,-66.556`: no overlap between the live official outlines near this spot
- **GONE** `CA-6538+CA-6540+CA-6541@area@46.544,-67.171`: no overlap between the live official outlines near this spot
- **GONE** `CA-6538+CA-6540@area@46.552,-67.216`: no overlap between the live official outlines near this spot
- **GONE** `CA-6538+CA-6541+CA-6550@area@46.500,-67.054`: no overlap between the live official outlines near this spot
- **GONE** `CA-6539+CA-6550+CA-6551@area@46.560,-66.121`: no overlap between the live official outlines near this spot
- **GONE** `CA-6539+CA-6551@area@46.560,-66.121`: no overlap between the live official outlines near this spot
- **GONE** `CA-6540+CA-6541+CA-6549@area@46.889,-67.404`: no overlap between the live official outlines near this spot
- **GONE** `CA-6541+CA-6542+CA-6549@area@47.321,-67.021`: no overlap between the live official outlines near this spot
- **GONE** `CA-6541+CA-6542+CA-6550@area@46.841,-66.687`: no overlap between the live official outlines near this spot
- **GONE** `CA-6541+CA-6542@area@47.321,-67.021`: no overlap between the live official outlines near this spot
- **GONE** `CA-6542+CA-6544+CA-6545@area@47.539,-66.504`: no overlap between the live official outlines near this spot
- **GONE** `CA-6542+CA-6545+CA-6549@area@47.489,-67.006`: no overlap between the live official outlines near this spot
- **GONE** `CA-6542+CA-6549@area@47.489,-67.006`: no overlap between the live official outlines near this spot
- **GONE** `CA-6542+CA-6550+CA-6551@area@46.824,-65.789`: no overlap between the live official outlines near this spot
- **GONE** `CA-6542+CA-6551@area@46.997,-65.558`: no overlap between the live official outlines near this spot
- **GONE** `CA-6545+CA-6546+CA-6549@area@47.513,-67.392`: no overlap between the live official outlines near this spot
- **GONE** `CA-6545+CA-6549@area@47.528,-67.165`: no overlap between the live official outlines near this spot
- **GONE** `CA-6546+CA-6547+CA-6549@area@47.472,-67.393`: no overlap between the live official outlines near this spot
- **GONE** `CA-6546+CA-6547@area@47.791,-68.383`: no overlap between the live official outlines near this spot
- **GONE** `CA-6547+CA-6548@area@47.490,-68.476`: no overlap between the live official outlines near this spot

The 2-fer file was not changed. A person and the club waiting room decide.
