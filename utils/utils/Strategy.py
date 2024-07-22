BSMR = """{
    "benchmark_spell": "",
    "benchmark_ticker": "SPY",
    "description": "",
    "incantation": {
        "condition": {
            "condition_type": "SingleCondition",
            "for_days": 1,
            "greater_than": true,
            "lh_days_ago": 0,
            "lh_indicator": {
                "type": "RelativeStrengthIndex",
                "window": 10
            },
            "lh_ticker_symbol": "TQQQ",
            "rh_bias": 0.0,
            "rh_days_ago": 0,
            "rh_indicator": {
                "type": "CumulativeReturn",
                "window": 0
            },
            "rh_ticker_symbol": "",
            "rh_value": 79.0,
            "rh_value_int": 0,
            "rh_weight": 1.0,
            "type": "IndicatorAndNumber"
        },
        "else_comment": "",
        "else_incantation": {
            "condition": {
                "condition_type": "SingleCondition",
                "for_days": 1,
                "greater_than": false,
                "lh_days_ago": 0,
                "lh_indicator": {
                    "type": "CumulativeReturn",
                    "window": 6
                },
                "lh_ticker_symbol": "TQQQ",
                "rh_bias": 0.0,
                "rh_days_ago": 0,
                "rh_indicator": {
                    "type": "CumulativeReturn",
                    "window": 0
                },
                "rh_ticker_symbol": "",
                "rh_value": -12.0,
                "rh_value_int": 0,
                "rh_weight": 1.0,
                "type": "IndicatorAndNumber"
            },
            "else_comment": "",
            "else_incantation": {
                "condition": {
                    "condition_type": "SingleCondition",
                    "for_days": 1,
                    "greater_than": true,
                    "lh_days_ago": 0,
                    "lh_indicator": {
                        "type": "MaxDrawdown",
                        "window": 10
                    },
                    "lh_ticker_symbol": "QQQ",
                    "rh_bias": 0.0,
                    "rh_days_ago": 0,
                    "rh_indicator": {
                        "type": "CumulativeReturn",
                        "window": 0
                    },
                    "rh_ticker_symbol": "",
                    "rh_value": 6.0,
                    "rh_value_int": 0,
                    "rh_weight": 1.0,
                    "type": "IndicatorAndNumber"
                },
                "else_comment": "",
                "else_incantation": {
                    "condition": {
                        "condition_type": "SingleCondition",
                        "for_days": 1,
                        "greater_than": true,
                        "lh_days_ago": 0,
                        "lh_indicator": {
                            "type": "MaxDrawdown",
                            "window": 10
                        },
                        "lh_ticker_symbol": "TMF",
                        "rh_bias": 0.0,
                        "rh_days_ago": 0,
                        "rh_indicator": {
                            "type": "CumulativeReturn",
                            "window": 0
                        },
                        "rh_ticker_symbol": "",
                        "rh_value": 7.0,
                        "rh_value_int": 0,
                        "rh_weight": 1.0,
                        "type": "IndicatorAndNumber"
                    },
                    "else_comment": "",
                    "else_incantation": {
                        "condition": {
                            "condition_type": "SingleCondition",
                            "for_days": 1,
                            "greater_than": true,
                            "lh_days_ago": 0,
                            "lh_indicator": {
                                "type": "CurrentPrice",
                                "window": 0
                            },
                            "lh_ticker_symbol": "QQQ",
                            "rh_bias": 0.0,
                            "rh_days_ago": 0,
                            "rh_indicator": {
                                "type": "MovingAverage",
                                "window": 25
                            },
                            "rh_ticker_symbol": "QQQ",
                            "rh_value": 0.0,
                            "rh_value_int": 0,
                            "rh_weight": 1.0,
                            "type": "BothIndicators"
                        },
                        "else_comment": "",
                        "else_incantation": {
                            "condition": {
                                "condition_type": "SingleCondition",
                                "for_days": 1,
                                "greater_than": true,
                                "lh_days_ago": 0,
                                "lh_indicator": {
                                    "type": "RelativeStrengthIndex",
                                    "window": 60
                                },
                                "lh_ticker_symbol": "SPY",
                                "rh_bias": 0.0,
                                "rh_days_ago": 0,
                                "rh_indicator": {
                                    "type": "CumulativeReturn",
                                    "window": 0
                                },
                                "rh_ticker_symbol": "",
                                "rh_value": 50.0,
                                "rh_value_int": 0,
                                "rh_weight": 1.0,
                                "type": "IndicatorAndNumber"
                            },
                            "else_comment": "",
                            "else_incantation": {
                                "condition": {
                                    "condition_type": "SingleCondition",
                                    "for_days": 1,
                                    "greater_than": false,
                                    "lh_days_ago": 0,
                                    "lh_indicator": {
                                        "type": "RelativeStrengthIndex",
                                        "window": 200
                                    },
                                    "lh_ticker_symbol": "IEF",
                                    "rh_bias": 0.0,
                                    "rh_days_ago": 0,
                                    "rh_indicator": {
                                        "type": "RelativeStrengthIndex",
                                        "window": 200
                                    },
                                    "rh_ticker_symbol": "TLT",
                                    "rh_value": 0.0,
                                    "rh_value_int": 0,
                                    "rh_weight": 1.0,
                                    "type": "BothIndicators"
                                },
                                "else_comment": "",
                                "else_incantation": null,
                                "incantation_type": "IfElse",
                                "name": "",
                                "then_comment": "",
                                "then_incantation": {
                                    "condition": {
                                        "condition_type": "SingleCondition",
                                        "for_days": 1,
                                        "greater_than": true,
                                        "lh_days_ago": 0,
                                        "lh_indicator": {
                                            "type": "RelativeStrengthIndex",
                                            "window": 45
                                        },
                                        "lh_ticker_symbol": "BND",
                                        "rh_bias": 0.0,
                                        "rh_days_ago": 0,
                                        "rh_indicator": {
                                            "type": "RelativeStrengthIndex",
                                            "window": 45
                                        },
                                        "rh_ticker_symbol": "SPY",
                                        "rh_value": 0.0,
                                        "rh_value_int": 0,
                                        "rh_weight": 1.0,
                                        "type": "BothIndicators"
                                    },
                                    "else_comment": "",
                                    "else_incantation": null,
                                    "incantation_type": "IfElse",
                                    "name": "",
                                    "then_comment": "",
                                    "then_incantation": {
                                        "incantation_type": "Ticker",
                                        "name": "",
                                        "symbol": "TQQQ"
                                    }
                                }
                            },
                            "incantation_type": "IfElse",
                            "name": "",
                            "then_comment": "",
                            "then_incantation": {
                                "condition": {
                                    "condition_type": "SingleCondition",
                                    "for_days": 1,
                                    "greater_than": true,
                                    "lh_days_ago": 0,
                                    "lh_indicator": {
                                        "type": "RelativeStrengthIndex",
                                        "window": 45
                                    },
                                    "lh_ticker_symbol": "BND",
                                    "rh_bias": 0.0,
                                    "rh_days_ago": 0,
                                    "rh_indicator": {
                                        "type": "RelativeStrengthIndex",
                                        "window": 45
                                    },
                                    "rh_ticker_symbol": "SPY",
                                    "rh_value": 0.0,
                                    "rh_value_int": 0,
                                    "rh_weight": 1.0,
                                    "type": "BothIndicators"
                                },
                                "else_comment": "",
                                "else_incantation": null,
                                "incantation_type": "IfElse",
                                "name": "",
                                "then_comment": "",
                                "then_incantation": {
                                    "incantation_type": "Ticker",
                                    "name": "",
                                    "symbol": "TQQQ"
                                }
                            }
                        },
                        "incantation_type": "IfElse",
                        "name": "",
                        "then_comment": "",
                        "then_incantation": {
                            "incantation_type": "Ticker",
                            "name": "",
                            "symbol": "TQQQ"
                        }
                    },
                    "incantation_type": "IfElse",
                    "name": "",
                    "then_comment": "",
                    "then_incantation": null
                },
                "incantation_type": "IfElse",
                "name": "",
                "then_comment": "",
                "then_incantation": null
            },
            "incantation_type": "IfElse",
            "name": "",
            "then_comment": "",
            "then_incantation": {
                "condition": {
                    "condition_type": "SingleCondition",
                    "for_days": 1,
                    "greater_than": true,
                    "lh_days_ago": 0,
                    "lh_indicator": {
                        "type": "CumulativeReturn",
                        "window": 1
                    },
                    "lh_ticker_symbol": "TQQQ",
                    "rh_bias": 0.0,
                    "rh_days_ago": 0,
                    "rh_indicator": {
                        "type": "CumulativeReturn",
                        "window": 0
                    },
                    "rh_ticker_symbol": "",
                    "rh_value": 5.5,
                    "rh_value_int": 0,
                    "rh_weight": 1.0,
                    "type": "IndicatorAndNumber"
                },
                "else_comment": "",
                "else_incantation": {
                    "condition": {
                        "condition_type": "SingleCondition",
                        "for_days": 1,
                        "greater_than": false,
                        "lh_days_ago": 0,
                        "lh_indicator": {
                            "type": "RelativeStrengthIndex",
                            "window": 10
                        },
                        "lh_ticker_symbol": "TQQQ",
                        "rh_bias": 0.0,
                        "rh_days_ago": 0,
                        "rh_indicator": {
                            "type": "CumulativeReturn",
                            "window": 0
                        },
                        "rh_ticker_symbol": "",
                        "rh_value": 32.0,
                        "rh_value_int": 0,
                        "rh_weight": 1.0,
                        "type": "IndicatorAndNumber"
                    },
                    "else_comment": "",
                    "else_incantation": {
                        "condition": {
                            "condition_type": "SingleCondition",
                            "for_days": 1,
                            "greater_than": false,
                            "lh_days_ago": 0,
                            "lh_indicator": {
                                "type": "MaxDrawdown",
                                "window": 10
                            },
                            "lh_ticker_symbol": "TMF",
                            "rh_bias": 0.0,
                            "rh_days_ago": 0,
                            "rh_indicator": {
                                "type": "CumulativeReturn",
                                "window": 0
                            },
                            "rh_ticker_symbol": "",
                            "rh_value": 7.0,
                            "rh_value_int": 0,
                            "rh_weight": 1.0,
                            "type": "IndicatorAndNumber"
                        },
                        "else_comment": "",
                        "else_incantation": null,
                        "incantation_type": "IfElse",
                        "name": "",
                        "then_comment": "",
                        "then_incantation": {
                            "incantation_type": "Ticker",
                            "name": "",
                            "symbol": "TQQQ"
                        }
                    },
                    "incantation_type": "IfElse",
                    "name": "",
                    "then_comment": "",
                    "then_incantation": {
                        "incantation_type": "Ticker",
                        "name": "",
                        "symbol": "TQQQ"
                    }
                },
                "incantation_type": "IfElse",
                "name": "",
                "then_comment": "",
                "then_incantation": {
                    "incantation_type": "Ticker",
                    "name": "",
                    "symbol": "UVXY"
                }
            }
        },
        "incantation_type": "IfElse",
        "name": "BSMR",
        "then_comment": "",
        "then_incantation": {
            "incantation_type": "Ticker",
            "name": "",
            "symbol": "UVXY"
        }
    },
    "name": "BSMR",
    "slippage_bps": 5,
    "threshold": 5,
    "trading_type": "Threshold",
    "version": 2
}"""