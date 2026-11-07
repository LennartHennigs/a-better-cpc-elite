# CPC to ZX Spectrum routine map (generated)

The CPC port is a Spectrum port, so most game logic has the same instruction skeleton on both. `tools/spectrum_map.py` matched
routines of `src/elite/*.asm` against the blocks of the Spectrum SkoolKit disassembly (`work/ext_msx/skoolkit/src/elite.skool`, by
Rasmus-M) by comparing instruction skeletons (immediates, addresses and offsets masked) with difflib; a second pass followed the
call graph from confident pairs (`prop`). A pair is listed when the ratio is at least 0.85 (propagated: 0.70), the margin over the
runner-up is at least 0.05 and the match is mutual best. Read the Spectrum commentary at the given address in `elite.skool`:
`grep -n '^c\$ADDR' work/ext_msx/skoolkit/src/elite.skool`.

What is in `src/elite/` (byte-exact, `tools/check_src.sh`):
- Generic labels with a confident Spectrum name were renamed (maps in `tools/rename_maps/2026-11-07-spectrum-*.txt`, applied by
  `tools/apply_spectrum_names.py` and `tools/rename_dat.py`), including Fessor's `todo_*` placeholders that have an exact counterpart.
- Every pair has a `; ZX Spectrum: name (&ADDR) ratio` line above its label.
- About 170 routines carry our own comment (maths, divides, square root, circle/disc code, text engine, charts, trade, ship movement, spawning);
  the wording is ours, written from the code, with the Spectrum I/O descriptions as a check. No Spectrum commentary is copied.
- Pre-change copies of the sources: `work/backup_src_pre_spectrum/`. Fessor's other names were left alone.

Disagreements: Fessor's `todoOverheating` (`&6812`) matches the Spectrum's "end the demo once a counter wraps" at 0.94; the code adds 2 to the
disc radius counter and bumps `CockpitTemp` and sets `GameOverFlag` when it wraps, so the CPC reading (overheating) was kept. Fessor's
`chkAltitude` is the dashboard compass update in the Spectrum disassembly. His ship names (`shipdatAlloy`, `shipdatSplinter`, ...) differ from
the Spectrum labels for several blueprints (the CPC `shipdatAlloy` is the Spectrum splinter, `shipdatSplinter` the boulder).

## Routines

| CPC file | CPC address | CPC label | Spectrum address | Spectrum label | ratio | how |
|---|---|---|---|---|---|---|
| common2x | &CFDC | circle_plot_g2_row | $925F | circle_plot_g2_row | 0.91 | direct |
| common2x | &E651 | circle_plot_pixel | $90CC | circle_plot_pixel | 0.92 | direct |
| common2x | &EE0A | squared_distance_to_cursor | $DFCE | squared_distance_to_cursor | 1.00 | direct |
| common2x | &EE26 | abs_difference | $DFEA | abs_difference | 1.00 | prop |
| common2x | &EE32 | finalize_distance | $DFF2 | finalize_distance | 0.92 | direct |
| common2x | &EE45 | mul_a_by_d | $E009 | mul_a_by_d | 1.00 | direct |
| common2x | &EE58 | name_planet | $E01C | generate_system_name | 1.00 | direct |
| common2x | &EEC8 | generatePlanetstats | $E08C | generate_system_data | 1.00 | direct |
| common2x | &F788 | circle_plot_g3_row | $917B | circle_plot_g3_row | 0.92 | direct |
| common2x | &F7AE | circle_plot_hbyte_l | $91AC | circle_plot_hbyte_l | 0.92 | direct |
| common2x | &F7C2 | LAB_ram_f7c2 | $91C0 | circle_plot_hbyte_r | 0.89 | direct |
| common2x | &FDFA | - | $D37D | pad_number_field | 0.91 | direct |
| common2x | &FE51 | SBC_HLDE | $D3CE | cp_hl_de | 1.00 | prop |
| common2x | &FE56 | getMoney | $D3D3 | add_cash | 1.00 | direct |
| common2x | &FE80 | tryPayForGood | $D3FD | subtract_cash | 1.00 | direct |
| common2x | &FEA8 | useJumpTokens1 | $D7B5 | print_control_code | 0.90 | direct |
| common2x | &FF91 | printFlightDigramsReducedRandom | $D885 | print_flavour_phrase | 1.00 | direct |
| commonxx | &2063 | chkMissions | $7278 | resume_screen_after_load | 0.91 | direct |
| commonxx | &20DA | circle_run_up | $86B8 | circle_run_up | 1.00 | prop |
| commonxx | &20E6 | circle_run_down | $86C4 | circle_run_down | 1.00 | prop |
| commonxx | &21CF | GetSquareforAinDE | $87BF | lookup_square | 1.00 | direct |
| commonxx | &21E5 | ce2func15 | $87D4 | circle_arc_segment | 1.00 | direct |
| commonxx | &220F | ce2func17 | $87FE | circle_fill_vert | 1.00 | direct |
| commonxx | &2352 | ce2func33 | $893F | circle_fill_steep_diag2 | 1.00 | direct |
| commonxx | &2398 | ce2func35 | $8985 | circle_horiz_end | 0.97 | direct |
| commonxx | &23B6 | ce2func36 | $89A1 | circle_horiz_end_mirror | 0.95 | direct |
| commonxx | &23D8 | ce2func38 | $89C3 | circle_seed_arc_regs | 1.00 | direct |
| commonxx | &23FA | ce2func40 | $89EF | circle_point_addr_right | 0.71 | prop |
| commonxx | &23FA | ce2func40 | $89EF | circle_point_addr_right | 0.71 | prop |
| commonxx | &2419 | ce2func41 | $8A16 | circle_run_setup_step | 1.00 | direct |
| commonxx | &2428 | ce2func42 | $8A25 | circle_run_setup_addr | 1.00 | direct |
| commonxx | &257E | ce2func57stack | $8ACD | circle_half_chord | 1.00 | direct |
| commonxx | &26C5 | ce2func78 | $8FB8 | circle_outline_edge_left | 1.00 | direct |
| commonxx | &2ADB | execSelectedKeyFunctions | $813E | call_d000_jump_table | 0.88 | direct |
| commonxx | &34D4 | shuffle_particle_table | $7E6D | shuffle_particle_table | 1.00 | direct |
| commonxx | &35AE | dashboard_and_special_keys | $9A40 | dashboard_and_special_keys | 0.97 | direct |
| commonxx | &3678 | destroy_cargo_unit | $D21F | destroy_cargo_unit | 1.00 | direct |
| commonxx | &383F | meLaunchEscapePod | $9C1C | launch_escape_pod | 0.91 | direct |
| commonxx | &3A28 | - | $D298 | new_game | 0.85 | direct |
| commonxx | &3A84 | LocalChart | $EC58 | draw_local_chart | 0.93 | direct |
| commonxx | &3AFB | setCalltoHLnGenerate | $ECD2 | for_each_system_in_window | 0.89 | direct |
| commonxx | &3C0F | drawPlanetnames | $ED78 | draw_system_name | 0.96 | direct |
| commonxx | &3DDA | notOnAChartscreen | $DF60 | find_nearest_system | 0.90 | direct |
| commonxx | &3F03 | printTokenAndToken0x20 | $E29E | print_token_space | 1.00 | prop |
| commonxx | &3F21 | printFollowingTokenWithSpace | $E2BC | tab_to_column | 1.00 | direct |
| commonxx | &4030 | todoReturnPressed | $E34C | commodity_is_tonnes | 0.88 | prop |
| commonxx | &41AA | SetTableBegintoAofHL | $EB3E | add_a_to_hl | 1.00 | prop |
| commonxx | &41BD | printNumber | $D2E1 | print_byte | 0.87 | direct |
| commonxx | &4209 | getMoneyinHLDE | $D32D | print_cash | 0.86 | direct |
| commonxx | &43A3 | printEconomy | $EEA8 | sysdata_print_economy | 0.90 | direct |
| commonxx | &440B | printfoundString | $D48E | recursive_other_token_loop | 1.00 | direct |
| commonxx | &4438 | parseToken | $D470 | print_other_token | 1.00 | direct |
| commonxx | &45A1 | print_two_letter_token | $D59C | print_two_letter_token | 1.00 | direct |
| commonxx | &45B9 | expandDescription | $D5B4 | other_token_92_to_128 | 1.00 | direct |
| commonxx | &45E6 | text_rng | $D5E1 | text_rng | 1.00 | direct |
| commonxx | &469C | buffer_justified_char | $D6B9 | buffer_justified_char | 0.99 | direct |
| commonxx | &4742 | begin_justified_text | $D75A | begin_justified_text | 1.00 | direct |
| commonxx | &476B | SUB_ram_476b | $D783 | - | 1.00 | direct |
| commonxx | &4789 | SUB_ram_4789 | $D7A1 | - | 1.00 | direct |
| commonxx | &4798 | printAlienRace | $EECE | sysdata_print_species | 0.89 | direct |
| commonxx | &47E4 | printPlanetsRadius | $EF21 | sysdata_print_radius | 1.00 | direct |
| commonxx | &47FA | CompareHLtoSEED | $EF37 | - | 0.91 | direct |
| commonxx | &480B | MarketPrices | $EF48 | show_market_prices | 0.98 | direct |
| commonxx | &4910 | status_print_equip | $F068 | status_print_equip | 1.00 | direct |
| commonxx | &4922 | prListEquippedLasers | $F07A | status_print_laser | 0.87 | direct |
| commonxx | &4AEE | SUB_ram_4aee | $DAB4 | - | 1.00 | direct |
| commonxx | &4B11 | LAB_ram_4b11 | $DAD7 | - | 1.00 | direct |
| commonxx | &4BC1 | resetInflightMessagesFlags | $DB91 | - | 1.00 | direct |
| commonxx | &4CAA | randomizeGalSeed | $DC83 | rotate_word_left | 1.00 | direct |
| commonxx | &526E | normalize_position_component | $9ECF | normalize_position_component | 1.00 | direct |
| commonxx | &5290 | approx_sqrt_16bit | $9EF1 | approx_sqrt_16bit | 1.00 | direct |
| commonxx | &52A9 | sqrt_approx_rescale_256 | $9F0A | sqrt_approx_rescale_256 | 1.00 | direct |
| commonxx | &52B7 | sqrt_approx_core | $9F18 | sqrt_approx_core | 1.00 | direct |
| commonxx | &52E0 | todoSomethingwithSine | $9F41 | tidy_vector | 0.83 | prop |
| commonxx | &52E0 | todoSomethingwithSine | $9F41 | tidy_vector | 0.83 | prop |
| commonxx | &53E8 | move_ship_forward | $A04B | move_ship_forward | 1.00 | direct |
| commonxx | &5413 | multiply_speed_nosev | $A076 | multiply_speed_nosev | 1.00 | direct |
| commonxx | &5448 | rotate_orientation_vector | $A0AB | rotate_orientation_vector | 1.00 | direct |
| commonxx | &549A | todoCalcAngle | $A0FD | combine_vector_rotation_rate | 0.81 | prop |
| commonxx | &549A | todoCalcAngle | $A0FD | combine_vector_rotation_rate | 0.81 | prop |
| commonxx | &54C5 | calcMatrixBankingClimbing | $A127 | rotate_orientation_vectors | 0.95 | direct |
| commonxx | &550E | MVIT | $A173 | rotate_and_step_ship | 0.85 | direct |
| commonxx | &561A | reshuffle_rate_bits | $A281 | reshuffle_rate_bits | 1.00 | prop |
| commonxx | &5624 | drawIntroShip | $A28D | draw_title_ship | 1.00 | direct |
| commonxx | &5812 | cache_explosion_screen_pos | $A8AC | cache_explosion_screen_pos | 1.00 | direct |
| commonxx | &5844 | chkEntityFiresLaser | $A8DE | draw_laser_only | 1.00 | direct |
| commonxx | &5976 | getEntryfromTable | $AA10 | check_face_visible | 1.00 | direct |
| commonxx | &5A72 | mult_b_c_msb | $AB0B | mult_b_c_msb | 1.00 | direct |
| commonxx | &5A85 | mult_b_coord_scaled | $AB1E | mult_b_coord_scaled | 1.00 | direct |
| commonxx | &5A9B | mult_b_c | $AB34 | mult_b_c | 1.00 | direct |
| commonxx | &5B27 | rotate_vertex_axis_cached | $ABC0 | rotate_vertex_axis_cached | 1.00 | direct |
| commonxx | &5B68 | face_normal_component | $AC01 | face_normal_component | 1.00 | direct |
| commonxx | &5BD0 | div_de_h | $AC69 | div_de_h | 0.92 | direct |
| commonxx | &5DB6 | lookup_vertex_coords | $AE50 | lookup_vertex_coords | 1.00 | direct |
| commonxx | &6096 | - | $84D9 | refresh_dashboard_bars | 0.97 | direct |
| commonxx | &61B0 | chkAltitude | $81A9 | position_tracked_markers | 1.00 | direct |
| commonxx | &6278 | chalt5 | $8271 | load_and_divide_position_component | 1.00 | prop |
| commonxx | &62B7 | chalt11 | $82BB | divide_scale_8_and_sign | 0.86 | direct |
| commonxx | &62DE | chalt15 | $82D7 | scale_distance_and_step_busy_flag | 0.82 | prop |
| commonxx | &62DE | chalt15 | $82D7 | scale_distance_and_step_busy_flag | 0.82 | prop |
| commonxx | &6525 | BCdiv16 | $96C5 | shift_bc_right | 1.00 | direct |
| commonxx | &66C5 | force_loading_busy_state | $988E | force_loading_busy_state | 1.00 | direct |
| commonxx | &66E5 | chkCanDockStation | $717B | handle_demo_fire_key | 0.91 | direct |
| commonxx | &671E | nudge_tracked_marker | $71C0 | nudge_tracked_marker | 1.00 | direct |
| commonxx | &6742 | half_diff_ship_marker | $71E4 | half_diff_ship_marker | 1.00 | prop |
| commonxx | &6751 | handle_chart_cursor_keys | $71F3 | handle_chart_cursor_keys | 1.00 | direct |
| commonxx | &6812 | todoOverheating | $75C0 | set_demo_message_flag | 0.94 | direct |
| commonxx | &684D | moveSpaceStation | $7861 | fly_ship0_to_origin | 1.00 | direct |
| commonxx | &6AA6 | divide_signed | $77A0 | divide_signed | 0.91 | direct |
| commonxx | &6AF3 | divide_underflow | $77ED | divide_underflow | 1.00 | direct |
| commonxx | &6B10 | divide_overflow | $780A | divide_overflow | 0.91 | direct |
| commonxx | &6B37 | LAB_ram_6b37 | $7831 | divide_underflow_overflow | 0.87 | direct |
| commonxx | &7038 | drawDustParticles | $7C92 | erase_starfield | 0.88 | direct |
| commonxx | &7071 | dust74 | $7CC9 | mul_a_by_c_loop | 1.00 | direct |
| commonxx | &716F | - | $9341 | unused_end_ring_transition | 0.93 | direct |
| commonxx | &719D | alt_animated_effect_reset | $9369 | alt_animated_effect_reset | 1.00 | direct |
| commonxx | &71AF | seed_starfield | $937B | seed_starfield | 1.00 | direct |
| commonxx | &737E | cleanShipSlots | $9509 | reset_ship_slots_1_to_7 | 1.00 | direct |
| commonxx | &7616 | - | $AECC | init_ship_calculations | 0.98 | direct |
| commonxx | &7670 | diff_of_products | $AF22 | diff_of_products | 0.82 | prop |
| commonxx | &7670 | diff_of_products | $AF22 | diff_of_products | 0.82 | prop |
| commonxx | &76F6 | div_hl_a_de | $AFA8 | div_hl_a_de | 0.77 | prop |
| commonxx | &76F6 | div_hl_a_de | $AFA8 | div_hl_a_de | 0.77 | prop |
| commonxx | &77D5 | calculate_visibility | $BD5F | calculate_visibility | 1.00 | direct |
| commonxx | &780B | mult_2_A_EC | $BD95 | mult_2_A_EC | 1.00 | direct |
| commonxx | &79C1 | SpawnMyRemains | $B618 | reset_all_ships | 0.90 | direct |
| commonxx | &7B41 | getRandomNumber | $B799 | rand_no | 1.00 | direct |
| commonxx | &7EE4 | mult_a_c | $B2F0 | mult_a_c | 1.00 | direct |
| commonxx | &809C | spawnCommandParser | $B867 | ship_action | 1.00 | direct |
| commonxx | &8168 | - | $B936 | find_free_ship_slot | 0.95 | direct |
| commonxx | &817F | trySpawnAnotherEntity | $B94A | spawn_ship_at_origin | 1.00 | direct |
| commonxx | &81A0 | spawnCommand1 | $B96B | create_ship_at_origin | 1.00 | direct |
| commonxx | &826A | - | $BA3F | - | 0.87 | direct |
| commonxx | &828D | switchNNegVectors | $BA58 | - | 1.00 | direct |
| commonxx | &82B8 | setDirectionofEntity | $BA83 | - | 1.00 | prop |
| commonxx | &82C9 | spawnCommand5 | $BA94 | - | 1.00 | direct |
| commonxx | &83EF | spawnCommand0 | $BBBA | - | 1.00 | direct |
| commonxx | &8432 | chkSpawnAsteroid | $BBF2 | finish_ship_and_escort | 0.91 | direct |
| commonxx | &8456 | cmd0ChkSendHostileAfterUs | $BC21 | pick_hostile_encounter | 1.00 | direct |
| commonxx | &897F | - | $A40F | check_ship_near_origin | 0.94 | direct |
| commonxx | &8AB7 | scaled_relative_pos_component | $A53F | scaled_relative_pos_component | 1.00 | direct |
| commonxx | &8AE7 | SUB_ram_8ae7 | $A568 | encode_ship_position_coord | 0.88 | direct |
| commonxx | &8BFE | combat_ai_refine_dist_zone | $A686 | combat_ai_refine_dist_zone | 1.00 | direct |
| commonxx | &8C15 | minus_4_a_b | $A69D | minus_4_a_b | 1.00 | direct |
| commonxx | &8C24 | dot_product_scale_factor | $A6AC | dot_product_scale_factor | 1.00 | direct |
| commonxx | &8E23 | dat_8E23 | $FCBA | handle_held_key | 0.97 | direct |
| commonxx | &8F68 | irki2_19 | $FF16 | clamp_speed_rate_max | 1.00 | direct |
| largeaxx | &0840 | BuyGoods | $E6AE | buy_cargo | 0.93 | direct |
| largeaxx | &08FF | getInputForFunctionHL | $E776 | read_trade_quantity | 0.87 | direct |
| largeaxx | &096D | buyQuantityofGood | $E7DB | buy_commodity_row | 0.94 | direct |
| largeaxx | &09CE | snapshot_trade_state | $E83C | snapshot_trade_state | 1.00 | direct |
| largeaxx | &09EF | restore_trade_state | $E85D | restore_trade_state | 1.00 | direct |
| largeaxx | &0A40 | SellGoods | $E8AE | sell_cargo | 0.97 | direct |
| largeaxx | &0AC0 | sellQuantityofGood | $E935 | sell_commodity_row | 1.00 | direct |
| largeaxx | &0FAF | SUB_ram_0faf | $DA5A | - | 0.86 | direct |

## Data tables identical on both machines (`tools/spectrum_data_map.py`)

| Spectrum label | Spectrum address | bytes | CPC address | CPC label |
|---|---|---|---|---|
| ship_asp | $61CC | 23 | &8FC7 | shipdatAspMk2 |
| ship_asteroid_v2 | $62F5 | 23 | &90F0 | shipdatRockHermit |
| ship_asteroid | $630C | 23 | &9107 | shipdatAsteroid |
| ship_canister | $63E5 | 23 | &91E0 | shipdatCargo |
| ship_cobra_mk_3_v1 | $6490 | 23 | &928B | SHIPDATSINGLETRADER |
| ship_fer_de_lance | $6689 | 23 | &9484 | shipdatFerDeLance |
| ship_missile | $67A6 | 23 | &95A1 | shipdatMissile |
| ship_splinter | $68A7 | 23 | &96A2 | shipdatAlloy |
| ship_python_v1 | $68E6 | 23 | &96E1 | SHIPDATBIGTRADER |
| ship_python_v2 | $68FD | 23 | &96F8 | shipdatPythonPirate |
| ship_sidewinder | $69F2 | 23 | &97ED | SHIPDATPIRATE1 |
| ship_coriolis | $6A9D | 23 | &9898 | shipdatCoriolis |
| ship_boulder | $6BBC | 23 | &99B7 | shipdatSplinter |
| ship_thargoid | $6C13 | 23 | &9A0E | shipdatThargoid |
| ship_krait | $6D32 | 23 | &9B2D | SHIPDATPIRATE2 |
| ship_viper | $6E1B | 23 | &9CC1 | shipdatViper |
| ship_thargon | $6EF8 | 23 | &9C16 | shipdatThargon |
| commodity_price_table | $701B | 68 | &2EF1 | dataStockItemsBaseParameter |
| equipment_price_table | $705F | 42 | &2F35 | Equipmentprices |
| starfield_particle_table | $7E8D | 81 | &34F4 | tblDustCoordinates |
| line_lookup_table | $AFF0 | 80 | &7BED | line_lookup_table |
| ship_init_data | $B83E | 31 | &8073 | shipEntityInitMatrixdata |
| sqr_table | $BE00 | 512 | &C600 | - |
| default_commander_data | $D23C | 92 | &39D1 | - |
| synonym_group_table | $D5F5 | 40 | &45FA | synonym_group_table |
| more_two_letter_tokens | $FD9B | 24 | &8DCA | FlightDigrams |
| two_letter_tokens | $FDB3 | 64 | &8DE2 | DockedDigrams |

The squares table `sqr_table` (`&C600`, 512 bytes) and the default commander (`&39D1`, 92 bytes) are identical too but have no label in `src/elite` yet.

## Not matched

Hardware routines (screen, keyboard, sound, loading, copy protection) differ by design; routines the CPC splits or joins differently from
the Spectrum also fail the whole-routine comparison. Candidates below 0.85 are in `work/spectrum_map/matches.tsv`.
