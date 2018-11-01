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
		alert("Invalid Public Key format.");
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
		// console.log(encrypted_text);
		
		$('#id_encrypted').val(encrypted_text);
		$('#id_public_key').val("NOPE. NICE TRY");
		// return false;
	});
});