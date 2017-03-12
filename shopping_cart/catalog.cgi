#!/usr/bin/perl -w

use warnings;
use strict;

use CGI;
use CGI::Carp qw(fatalsToBrowser);

my $query = CGI->new();

my $file = 'products.txt';
my $cart_file = '/tmp/cart.txt';
my ($session_id, $product_id, $quantity);

if ($query->param('product_id')) {
	if( $query->cookie('session_id')) {
		$session_id = $query->cookie('session_id');
	} else {
		$session_id = time . $$;
	}
	set_variables();
	add_to_cart();
	print_page_start();
	open_catalog();
	display_catalog();
	print_page_end();
} else {
	print_page_start();
	open_catalog();
	display_catalog();
	print_page_end();
}

sub set_variables {
	$product_id = $query->param('product_id');
	$quantity = $query->param('quantity');
}

sub add_to_cart {
	chdir;
	open (CART, '+>>', $cart_file) or die "Could not open? '$cart_file' $!:";
	flock CART, 2;
	seek CART, 0, 0;
	my @records  = <CART>;
	my @new_records = ();
	my $found = 'no';
	foreach my $record (@records) {
		chomp $record;
		my ($rec_session_id, $rec_product_id, $rec_quantity) = split /:/, $record;
		if (($session_id) eq $rec_session_id and ($product_id eq $rec_product_id)) {
			my $new_quantity = $quantity + $rec_quantity;
			my $new_record = "$session_id:$product_id:$new_quantity";
			$record = $new_record;
			$found = 'yes';
		}
		$record .= "\n";
		push @new_records, $record;
	}
	seek CART, 0, 0;
	truncate CART, 0;
	print CART @new_records;
	if ($found eq 'no') {
		print CART "$session_id:$product_id:$quantity\n";
	}
	close CART;
}

# this also creates a cookie which stores the session_id
sub print_page_start {
	
	if ($session_id) {
		my $cookie = $query->cookie(-name=>'session_id',-value=>$session_id);
		print $query->header(-cookie=>$cookie);
	}
	else {
		print $query->header;
	}

	print "<html>\n<head>\n<title>PC Product Catalog</title>\n";
	print "</head>\n<body>\n";
	print "<h1 align=\"center\">PC Product Catalog</h1>\n";
}

sub open_catalog {
	eval {
		open (CATALOG, '<', $file) or die "Cant open '$file' $!:";
	}
}

sub display_catalog {
	print "<div align=\"center\">\n";
	print "<table border=\"1\" cellpading=\"4\">\n";
	print "<tr>\n<th>Description</th>\n<th>Price</th>\n</tr>\n";
	#open (CATALOG, '<', $file) or die "Cant open '$file' $!:";
	while (my $line = <CATALOG>) {
		chomp $line;

		my ($product_id, $product_desc, $product_price) = split /:/, $line;
		print "<tr>\n";
		print "<form>\n";
		print "<input type=\"hidden\" NAME=\"product_id\" ";
		print "value=\"$product_id\" />\n";
		print "<td>$product_desc</td>\n<td>$product_price</td>\n";
		print "<td><input type=\"text\" name=\"quantity\" ";
		print "value=\"1\" size=\"2\" /></td>\n";
		print "<td><input type=\"submit\" value=\"add\" /></td>\n";
		print "</form>\n";
		print "</tr>\n";
	}
	print "</table>\n</div>\n";
}

sub print_page_end {
	print "<p><div align=\"center\"><b>";
	print "<a href=\"cart.cgi\">view cart</a></b></div></p>\n";
	print "</body>\n</html>\n";
}
