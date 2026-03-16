class TwseCli < Formula
  include Language::Python::Virtualenv

  desc "Agent-friendly CLI for Taiwan Stock Exchange (TWSE) OpenAPI"
  homepage "https://github.com/weirenlan/twse-cli"
  url "https://files.pythonhosted.org/packages/source/t/twse-cli/twse_cli-0.1.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "twse-cli", shell_output("#{bin}/twse version")
  end
end
