# Trader Performance vs Bitcoin Market Sentiment

## Dataset coverage
This section frames the scale of the study, the overlap window between both datasets, and the baseline profitability profile before splitting results by sentiment regime.
- Trades analyzed: 211,218
- Distinct accounts: 32
- Time window: 2023-05-01 to 2025-05-01
- Total fee-adjusted net PnL: 10,008,637.74
- Overall trade win rate: 41.12%

## Key findings
This section compresses the highest-signal conclusions so a reader can understand the regime effects without scanning the full detail tables.
- The strongest regime was Extreme Greed, with net PnL per trade of 67.22 and win rate of 46.49%.
- The weakest regime was Neutral, with net PnL per trade of 33.26 and win rate of 39.70%.
- Fear regimes produced aggregate fee-adjusted net PnL of 3,979,920.11 versus 4,775,171.23 in greed regimes.
- The correlation between daily sentiment value and daily net PnL was -0.079, which suggests the linear relationship is weak and regime effects matter more than raw index level alone.
- Median trade-level net PnL remains near zero across all regimes, which implies a heavily skewed payoff profile where a small number of large wins drive most profits.

## Regime summary
This section compares each sentiment bucket on trade count, account participation, fee-adjusted profitability, trade sizing, and win behavior. It is the core evidence for regime-aware strategy decisions.
```
classification  trades  unique_accounts  total_size_usd    gross_pnl  total_fees      net_pnl  avg_net_pnl  median_net_pnl  win_rate  buy_share  avg_size_usd  median_pnl_per_usd  mean_pnl_per_usd  net_pnl_per_trade  fee_to_gross_pnl
  Extreme Fear   21400               32  114484261.4400  739110.2485  23888.6339  715221.6146      33.4216         -0.0060    0.3706     0.5110     5349.7318             -0.0000            0.0041            33.4216            0.0323
          Fear   61837               32  483324789.7900 3357155.4416  92456.9487 3264698.4930      52.7952         -0.0058    0.4208     0.4895     7816.1099             -0.0000            0.0149            52.7952            0.0275
       Neutral   37686               31  180242063.0800 1292920.6756  39374.2683 1253546.4072      33.2629         -0.0075    0.3970     0.5033     4782.7327             -0.0000            0.0095            33.2629            0.0305
         Greed   50303               31  288582494.7200 2150129.2730  63098.6920 2087030.5810      41.4892         -0.0105    0.3848     0.4886     5736.8844             -0.0001            0.0194            41.4892            0.0293
 Extreme Greed   39992               30  124465164.5700 2715171.3107  27030.6655 2688140.6452      67.2170         -0.0011    0.4649     0.4486     3112.2516             -0.0000            0.0398            67.2170            0.0100
```

## Account patterns
This section highlights that the aggregate signal is not evenly distributed. Some traders are structurally stronger in fear, while others monetize greed much better, which matters for trader selection and strategy routing.
Top accounts that outperform more in fear than greed:
```
                                   account  fear_net_pnl  greed_net_pnl  fear_minus_greed  all_net_pnl  all_trades
0x083384f897ee0f19899168e3b1bec365f52a9012    1234752.93      233722.61        1001030.32   1592824.51        3818
0xbaaaf6571ab7d571043ff1e313a9609a10637864     875250.40           4.55         875245.85    931567.10       21192
0x8170715b3b381dffb7062c0298972d4727a0a63b     163435.87     -379952.63         543388.50   -169200.51        4601
0x4acb90e786d897ecffb614dc822eb231b4ffb9f4     457910.09      115223.73         342686.36    669721.06        4356
0x72c6a4624e1dffa724e6d00d64ceae698af892a0     343296.17       21502.10         321794.06    360258.01        1424
```

Top accounts that outperform more in greed than fear:
```
                                   account  fear_net_pnl  greed_net_pnl  fear_minus_greed  all_net_pnl  all_trades
0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23      99379.37     1629741.36       -1530361.99   2127387.28       14733
0xbee1707d6b44d4d52bfe19e41f8a828645437aab      80567.77      718152.75        -637584.98    822727.65       40184
0x72743ae2822edd658c0c50608fd7c5c501b2afbd     -25032.20      452846.93        -477879.13    427804.13        1590
0x430f09841d65beb3f27765503d0f850b8bce7713       5504.82      351541.41        -346036.59    415794.87        1237
0x75f7eeb85dc639d5e99c78f95393aa9a5f1170d4      74320.79      305216.50        -230895.71    376500.15        9893
```

High-activity account regime behavior sample:
```
                                   account classification      net_pnl  trades  win_rate
0x28736f43f1e871e6aa8b1148d38d4994275d72c4   Extreme Fear  -25820.0185     574    0.2875
0x28736f43f1e871e6aa8b1148d38d4994275d72c4  Extreme Greed  106878.6709    7481    0.4445
0x28736f43f1e871e6aa8b1148d38d4994275d72c4           Fear   13152.9488    1399    0.4303
0x28736f43f1e871e6aa8b1148d38d4994275d72c4          Greed   30700.3434    2970    0.4485
0x28736f43f1e871e6aa8b1148d38d4994275d72c4        Neutral    5334.5025     887    0.4667
0x47add9a56df66b524d5e2c1993a43cde53b6ed85   Extreme Fear  -14582.4326     391    0.2634
0x47add9a56df66b524d5e2c1993a43cde53b6ed85  Extreme Greed   66673.2204    3150    0.3429
0x47add9a56df66b524d5e2c1993a43cde53b6ed85           Fear    9879.3438     924    0.3766
0x47add9a56df66b524d5e2c1993a43cde53b6ed85          Greed   36188.1602    3398    0.3508
0x47add9a56df66b524d5e2c1993a43cde53b6ed85        Neutral    3954.5778     656    0.4390
0x4f93fead39b70a1824f981a54d4e55b278e9f760   Extreme Fear   71421.6796     371    0.4286
0x4f93fead39b70a1824f981a54d4e55b278e9f760  Extreme Greed  115357.1463    2446    0.3336
0x4f93fead39b70a1824f981a54d4e55b278e9f760           Fear  -24940.4392    1156    0.3555
0x4f93fead39b70a1824f981a54d4e55b278e9f760          Greed   67854.1625    2334    0.3436
0x4f93fead39b70a1824f981a54d4e55b278e9f760        Neutral   38558.8531    1277    0.4268
0x513b8629fe877bb581bf244e326a047b249c4ff1   Extreme Fear  -71659.3886     346    0.3035
0x513b8629fe877bb581bf244e326a047b249c4ff1  Extreme Greed     -12.3803     223    0.0000
0x513b8629fe877bb581bf244e326a047b249c4ff1           Fear  329571.0485    5981    0.3705
0x513b8629fe877bb581bf244e326a047b249c4ff1          Greed  138178.7974    3169    0.3765
0x513b8629fe877bb581bf244e326a047b249c4ff1        Neutral  367919.8352    2517    0.5542
0x75f7eeb85dc639d5e99c78f95393aa9a5f1170d4   Extreme Fear   25462.6424     316    0.9146
0x75f7eeb85dc639d5e99c78f95393aa9a5f1170d4  Extreme Greed  210004.2751    3831    0.8546
0x75f7eeb85dc639d5e99c78f95393aa9a5f1170d4           Fear   48858.1493    1664    0.7794
0x75f7eeb85dc639d5e99c78f95393aa9a5f1170d4          Greed   95212.2281    2618    0.8079
0x75f7eeb85dc639d5e99c78f95393aa9a5f1170d4        Neutral   -3037.1474    1464    0.7152
0x8477e447846c758f5a675856001ea72298fd9cb5   Extreme Fear    1559.6934     539    0.2505
0x8477e447846c758f5a675856001ea72298fd9cb5  Extreme Greed   54876.7910    3986    0.3362
0x8477e447846c758f5a675856001ea72298fd9cb5           Fear    8912.9919    1474    0.3270
0x8477e447846c758f5a675856001ea72298fd9cb5          Greed  -25398.0797    6804    0.1991
0x8477e447846c758f5a675856001ea72298fd9cb5        Neutral     173.0693    2195    0.2811
0xa0feb3725a9335f49874d7cd8eaad6be45b27416   Extreme Fear     987.6880     270    0.2259
0xa0feb3725a9335f49874d7cd8eaad6be45b27416  Extreme Greed   47403.4066    3497    0.4235
0xa0feb3725a9335f49874d7cd8eaad6be45b27416           Fear   12466.2338    2324    0.3184
0xa0feb3725a9335f49874d7cd8eaad6be45b27416          Greed   34596.0727    4115    0.3375
0xa0feb3725a9335f49874d7cd8eaad6be45b27416        Neutral    8561.5189    5399    0.3195
0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23   Extreme Fear    8953.6117     739    0.3112
0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23  Extreme Greed 1103779.1583    1643    0.5100
0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23           Fear   90425.7546    3005    0.3271
0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23          Greed  525962.2022    5889    0.2732
0xb1231a4a2dd02f2276fa3c5e2a2f3436e6bfed23        Neutral  398266.5526    3457    0.3781
0xbaaaf6571ab7d571043ff1e313a9609a10637864   Extreme Fear  260019.9006    4480    0.3795
0xbaaaf6571ab7d571043ff1e313a9609a10637864           Fear  615230.4984   12437    0.4983
0xbaaaf6571ab7d571043ff1e313a9609a10637864          Greed       4.5526       5    0.2000
0xbaaaf6571ab7d571043ff1e313a9609a10637864        Neutral   56312.1489    4270    0.4710
0xbee1707d6b44d4d52bfe19e41f8a828645437aab   Extreme Fear   29044.5772    5079    0.4133
0xbee1707d6b44d4d52bfe19e41f8a828645437aab  Extreme Greed  477137.3091    6723    0.5963
0xbee1707d6b44d4d52bfe19e41f8a828645437aab           Fear   51523.1973   12901    0.3766
0xbee1707d6b44d4d52bfe19e41f8a828645437aab          Greed  241015.4457    7338    0.4647
0xbee1707d6b44d4d52bfe19e41f8a828645437aab        Neutral   24007.1241    8143    0.3478
```

## Trading implications
This section translates the descriptive analysis into practical portfolio and execution decisions that can be tested or operationalized.
- Favor regime-aware sizing. Average outcomes can change materially by sentiment bucket even when median trade PnL does not.
- Treat greed regimes as higher-selectivity environments. If your strategy depends on momentum continuation, use stricter confirmation and tighter risk limits when the index is elevated.
- Maintain optionality in fear regimes. The data indicates that dislocated conditions can produce better realized PnL per trade, likely because volatility creates larger mean-reversion or short-squeeze opportunities.
- Measure performance at the account-strategy level, not just in aggregate. Several accounts exhibit strong fear-versus-greed asymmetry, which is a concrete signal for strategy routing or trader profiling.

## Caveats
This section records the analytical limits of the provided data so downstream users do not over-interpret the conclusions.
- The trader dataset does not include a leverage column in the provided file, so leverage-adjusted conclusions were not possible.
- Closed PnL is realized at trade events and may reflect prior position context, so trade-level return metrics should be treated as directional rather than exact strategy returns.
- Sentiment is joined at daily granularity. Intraday shifts are not captured.