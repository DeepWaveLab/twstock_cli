class TwstockCli < Formula
  include Language::Python::Virtualenv

  desc "Agent-friendly CLI for Taiwan Stock Exchange (TWSE) and Taipei Exchange (TPEX)"
  homepage "https://github.com/DeepWaveLab/twstock_cli"
  url "https://files.pythonhosted.org/packages/56/bd/ad31947483e5a937d994e865a2c94e161a27ac7565deb3f4f8cf6ae212fa/twstock_cli-0.1.2.tar.gz"
  sha256 "edf3ccbb81de54d943538e1be997f13822f90e189693ab0f0d04e64349b622bd"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "twstock-cli", shell_output("#{bin}/twstock version")
  end
end
