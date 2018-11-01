function encryptText(pubkey, textToEncrypt)
{
	try {
		var publicKey = forge.pki.publicKeyFromPem(pubkey);
		var secretMessage = textToEncrypt;
		var encrypted = publicKey.encrypt(secretMessage, "RSA-OAEP", {
					md: forge.md.sha256.create(),
					mgf1: forge.mgf1.create()
				});
		var mybase64 = forge.util.encode64(encrypted);
		return mybase64;
	} catch (err) {
		alert("Check console");
		console.log("Error caught. Handle this ", err);
	}
}

$(document).ready(function(){
	$('#transact_form_submit').click(function(){
		var public_key = $('#id_public_key').val();

		var $inputs = $('#transact_form :input');

		var values = {};
		$inputs.each(function() {
			if (this.name !== "encrypted" && this.name !== "csrfmiddlewaretoken" && this.name !== "otp" && this.name !== "" && this.name !== "public_key")
				values[this.name] = $(this).val();
		});

		values = JSON.stringify(values);
		encrypted_text = encryptText(public_key, values);
		console.log(encrypted_text);

		$('#id_encrypted').val(encrypted_text);
		return true;
	});
});
/*
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA20KEqfwK3+Hh20AtCdhT
1vSikhcepCarKozXlsiO0wxL7L22RooeJ7zSpALBSc27fGveN5DQ+PP/Fyq3+SiS
2Q/Mu1RkgIMiQvEhYqeOAe7bhcQJdjLaptAd0CNycnU+kHwZbtvi60TganrcThT1
hWz13+Gdy2OXRxeHk/Gzo2gr0Y1g6soLWcQC/0U7t9auToDZl2O5BsvltYPUjm+r
fq8xLAlOGzmHcQ3XMyB14044Eu4rNhgXKiXpLYM0Rm/a9BR4OTqtM/jheuC0e3Bs
IQ+v/jRdnd2L16i0DqgLuEFU5pThmZFP+EFa8trwqE+fpW809Ul+BYfg3SH3sfLm
twIDAQAB
-----END PUBLIC KEY-----
*/