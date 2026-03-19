class TwstockCli < Formula
  include Language::Python::Virtualenv

  desc "Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX)"
  homepage "https://github.com/DeepWaveLab/twstock_cli"
  url "https://files.pythonhosted.org/packages/c9/56/b8c96623f5a03bef565029af67cee1a935c03f361b6827ef86ec83e1e688/twstock_cli-0.1.4.tar.gz"
  sha256 "f629b3c5c69e673f7c50266a6fb402c3642a54151e52d4e7ffbf514b12c53da9"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "Usage", shell_output("#{bin}/twstock --help")
  end
end
