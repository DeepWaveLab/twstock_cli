class TwstockCli < Formula
  include Language::Python::Virtualenv

  desc "Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX)"
  homepage "https://github.com/weirenlan/twstock-cli"
  url "https://files.pythonhosted.org/packages/source/t/twstock-cli/twstock_cli-0.1.0.tar.gz"
  sha256 "PLACEHOLDER"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "twstock-cli", shell_output("#{bin}/twstock version")
  end
end
