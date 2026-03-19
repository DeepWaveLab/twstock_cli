class TwstockCli < Formula
  include Language::Python::Virtualenv

  desc "Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX)"
  homepage "https://github.com/DeepWaveLab/twstock_cli"
  url "https://files.pythonhosted.org/packages/03/6d/b46ce035351c15b0ad56aa66887bf817169fc0aa1e029ecbb91757ba1ce5/twstock_cli-0.1.3.tar.gz"
  sha256 "0b24f3cb71961c7f52e08c7082998ac20aa8384ef44e49c26ca4116f0b83719e"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Usage", shell_output("#{bin}/twstock --help")
  end
end
