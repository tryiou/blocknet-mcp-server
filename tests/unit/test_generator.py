"""Unit tests for the Generator module"""

from pathlib import Path

from scripts.generate.generator import DEFAULT_WRITE_PROTECTED, PREFIX_CONFIG, Generator
from scripts.generate.parser import ApiSpec, parse_api_docs


class TestGeneratorInit:
    """Tests for Generator initialization"""

    def test_generator_init_with_xbridge(self):
        gen = Generator("blocknet-api-docs/source/includes/_xbridge.md", "dx", "/tmp/output")
        assert gen.doc_path == Path("blocknet-api-docs/source/includes/_xbridge.md")
        assert gen.prefix == "dx"
        assert gen.output_dir == Path("/tmp/output")

    def test_generator_init_with_xrouter(self):
        gen = Generator("blocknet-api-docs/source/includes/_xrouter.md", "xr", "/tmp/output")
        assert gen.doc_path == Path("blocknet-api-docs/source/includes/_xrouter.md")
        assert gen.prefix == "xr"
        assert gen.output_dir == Path("/tmp/output")

    def test_prefix_config_loaded_dx(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        assert gen._config["name"] == "xbridge_mcp"
        assert gen._config["display_name"] == "XBridge"
        assert gen._config["client_class_name"] == "AsyncXBridgeClient"

    def test_prefix_config_loaded_xr(self):
        gen = Generator("path/to/docs.md", "xr", "/tmp/output")
        assert gen._config["name"] == "xrouter_mcp"
        assert gen._config["display_name"] == "XRouter"
        assert gen._config["client_class_name"] == "AsyncXRouterClient"

    def test_prefix_normalized_to_lowercase(self):
        gen = Generator("path/to/docs.md", "DX", "/tmp/output")
        assert gen.prefix == "dx"


class TestBuildServerConfig:
    """Tests for _build_server_config method"""

    def test_build_server_config_dx(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        config = gen._build_server_config()

        assert config["display_name"] == "XBridge"
        assert config["server_name"] == "XBridge MCP Server"
        assert config["env_prefix"] == "XBRIDGE_MCP"
        assert config["package_name"] == "xbridge_mcp"
        assert config["client_class_name"] == "AsyncXBridgeClient"
        assert config["tool_prefix"] == "dx"
        assert config["rpc_prefix"] == "dx"
        assert config["host"] == "localhost"
        assert config["port"] == 41414

    def test_build_server_config_xr(self):
        gen = Generator("path/to/docs.md", "xr", "/tmp/output")
        config = gen._build_server_config()

        assert config["display_name"] == "XRouter"
        assert config["server_name"] == "XRouter MCP Server"
        assert config["env_prefix"] == "XROUTER_MCP"
        assert config["package_name"] == "xrouter_mcp"
        assert config["client_class_name"] == "AsyncXRouterClient"
        assert config["tool_prefix"] == "xr"
        assert config["rpc_prefix"] == "xr"


class TestParseSampleParams:
    """Tests for _parse_sample_params method - type conversion fix"""

    def test_parse_true_boolean(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "xrGetTransaction TICKER true"})()
        result = gen._parse_sample_params(endpoint)
        assert result == [True]

    def test_parse_false_boolean(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "xrGetTransaction TICKER false"})()
        result = gen._parse_sample_params(endpoint)
        assert result == [False]

    def test_parse_integer(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "dxGetOrderBook TICKER 1 2"})()
        result = gen._parse_sample_params(endpoint)
        assert result == [1, 2]
        assert isinstance(result[0], int)
        assert isinstance(result[1], int)

    def test_parse_float(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "blocknet-cli dxGetTradingData 1.5"})()
        result = gen._parse_sample_params(endpoint)
        assert result == [1.5]
        assert isinstance(result[0], float)

    def test_parse_negative_number(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "blocknet-cli dxGetTradingData -10"})()
        result = gen._parse_sample_params(endpoint)
        assert result == [-10]
        assert isinstance(result[0], float)  # Generator converts all numbers to float

    def test_parse_string_ticker(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "blocknet-cli dxGetLocalTokens TICKER"})()
        result = gen._parse_sample_params(endpoint)
        assert result == ["TICKER"]

    def test_parse_single_param(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "blocknet-cli dxGetTrades TICKER"})()
        result = gen._parse_sample_params(endpoint)
        assert result == ["TICKER"]

    def test_parse_multiple_params_mixed_types(self):
        gen = Generator("path/to/docs.md", "dx", "/tmp/output")
        endpoint = type("obj", (object,), {"sample_request": "blocknet-cli dxGetOrderBook TICKER1 TICKER2 1440 true 10"})()
        result = gen._parse_sample_params(endpoint)
        assert result == ["TICKER1", "TICKER2", 1440, True, 10]
        assert isinstance(result[2], int)
        assert isinstance(result[3], bool)
        assert isinstance(result[4], int)


class TestPrefixConfig:
    """Tests for PREFIX_CONFIG constant"""

    def test_prefix_config_has_dx(self):
        assert "dx" in PREFIX_CONFIG
        assert PREFIX_CONFIG["dx"]["name"] == "xbridge_mcp"

    def test_prefix_config_has_xr(self):
        assert "xr" in PREFIX_CONFIG
        assert PREFIX_CONFIG["xr"]["name"] == "xrouter_mcp"

    def test_prefix_config_all_have_required_fields(self):
        for prefix, config in PREFIX_CONFIG.items():
            assert "name" in config
            assert "display_name" in config
            assert "client_class_name" in config
            assert "doc_path" in config


class TestWriteProtected:
    """Tests for write-protected endpoint filtering"""

    def test_dx_has_write_protected_endpoints(self):
        assert "dxMakeOrder" in DEFAULT_WRITE_PROTECTED["dx"]
        assert "dxTakeOrder" in DEFAULT_WRITE_PROTECTED["dx"]
        assert "dxCancelOrder" in DEFAULT_WRITE_PROTECTED["dx"]

    def test_xr_has_write_protected_endpoints(self):
        assert "xrUpdateNetworkServices" in DEFAULT_WRITE_PROTECTED["xr"]
        assert "xrConnect" in DEFAULT_WRITE_PROTECTED["xr"]
        assert "xrSendTransaction" in DEFAULT_WRITE_PROTECTED["xr"]

    def test_read_endpoints_not_in_write_protected(self):
        assert "dx_get_local_tokens" not in DEFAULT_WRITE_PROTECTED["dx"]
        assert "dx_get_network_tokens" not in DEFAULT_WRITE_PROTECTED["dx"]
        assert "xr_get_block_count" not in DEFAULT_WRITE_PROTECTED["xr"]


class TestGeneratorLoadSpec:
    """Tests for load_spec method"""

    def test_load_spec_returns_apispec(self):
        gen = Generator("blocknet-api-docs/source/includes/_xbridge.md", "dx", "/tmp/output")
        spec = gen.load_spec()

        assert isinstance(spec, ApiSpec)
        assert len(spec.endpoints) > 0
        assert spec.name == "xbridge_mcp"

    def test_load_spec_xrouter(self):
        gen = Generator("blocknet-api-docs/source/includes/_xrouter.md", "xr", "/tmp/output")
        spec = gen.load_spec()

        assert isinstance(spec, ApiSpec)
        assert len(spec.endpoints) > 0
        assert spec.name == "xrouter_mcp"

    def test_loaded_spec_stores_in_instance(self):
        gen = Generator("blocknet-api-docs/source/includes/_xbridge.md", "dx", "/tmp/output")
        spec = gen.load_spec()
        assert gen.spec is spec


class TestGeneratorHelpers:
    """Tests for helper methods"""

    def test_to_tool_name_via_spec(self):
        spec = parse_api_docs("blocknet-api-docs/source/includes/_xbridge.md", "dx")
        endpoint = spec.endpoints.get("dxGetLocalTokens")
        assert endpoint is not None
        assert endpoint.tool_name == "dxGetLocalTokens"

    def test_endpoint_params_have_python_types(self):
        spec = parse_api_docs("blocknet-api-docs/source/includes/_xbridge.md", "dx")
        endpoint = spec.endpoints.get("dxMakeOrder")
        assert endpoint is not None

        param_types = {p.name: p.python_type for p in endpoint.params}
        assert "maker" in param_types
        assert "taker" in param_types
        assert param_types["maker"] == "str"
        assert param_types["taker"] == "str"

    def test_error_codes_parsed_xr(self):
        spec = parse_api_docs("blocknet-api-docs/source/includes/_xrouter.md", "xr")
        # XRouter doc has no global error section, should load from _errors.md
        assert len(spec.error_codes) > 0, "Should have error codes from global _errors.md"
        # Spot-check common codes
        assert 1004 in spec.error_codes  # Bad request
        assert 1025 in spec.error_codes  # Invalid parameters
