Feature: Demo file parsing
  In order to analyze mine and others' performance in Dota 2
  As a developer and gamer
  I want to parse Dota 2 "demo" (replay) files

  Background:
    Given "skadi" is in PATH

  @wip
  Scenario: Verifying the replay
    When I issue the following command from the project root
      """
      skadi --search=$SKADI_ROOT/demos 12345678.dem
      """
    Then the output should contain the following sections:
      | Section   |
      | roster    |
      | frames    |
